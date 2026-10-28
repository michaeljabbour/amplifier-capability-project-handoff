"""Substantive checks on scoring, transfer isolation, safety and frozen records."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'evals'))
import run
from metrics import CRITERIA, paired_difference, parse_json, score_trial, validate_capture, validate_evidence, validate_judgment
from prompts import CAPTURE_SCHEMA, RESUME_SCHEMA, capture_prompt, resume_prompt
from providers import NoRedirect, ProviderError


def good_judgment():
    j={k:True for k in CRITERIA}
    j.update(leave_alone=None,critical_failure=False,explanation='Supported.',evidence_quotes=[{'source':'capture_note','quote':'A quote.'}])
    return j


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.fixtures=json.loads((ROOT/'evals/fixtures.json').read_text())

    def test_unauthorized_attempt_overrides_favorable_judge(self):
        s=score_trial({'judgment':good_judgment(),'unauthorized_write':True})
        self.assertFalse(s['resume_correct'])
        self.assertFalse(s['all_gates_pass'])
        self.assertTrue(s['critical_failure'])

    def test_unnecessary_clean_case_write_fails_even_if_judge_misses_it(self):
        j=good_judgment();j['leave_alone']=True
        s=score_trial({'judgment':j,'leave_alone_violation':True})
        self.assertTrue(s['resume_correct'])
        self.assertFalse(s['all_gates_pass'])

    def test_error_cannot_disappear_from_denominator(self):
        s=score_trial({'error':'transport failure'})
        self.assertTrue(s['ungraded'])
        self.assertFalse(s['resume_correct'])
        self.assertFalse(s['all_gates_pass'])

    def test_fresh_resumer_does_not_receive_session_or_capture_only_file(self):
        f=copy.deepcopy(self.fixtures[0])
        f['session']=[{'text':'PRIVATE_HISTORY_SENTINEL'}]
        f['capture_files']['hidden.txt']={'text':'CAPTURE_ONLY_SENTINEL'}
        text=resume_prompt(f,'Only this handoff transfers.')
        self.assertNotIn('PRIVATE_HISTORY_SENTINEL',text)
        self.assertNotIn('CAPTURE_ONLY_SENTINEL',text)
        self.assertNotIn('SKILL.md',text)
        self.assertNotIn('expected',text)

    def test_answer_key_not_in_evaluated_capture_prompt(self):
        f=copy.deepcopy(self.fixtures[0]);f['expected']='SECRET_KEY_SENTINEL'
        text=capture_prompt(f)
        self.assertNotIn('SECRET_KEY_SENTINEL',text)
        self.assertNotIn('decision_fidelity',text)
        self.assertNotIn('critical_failure',text)

    def test_capture_schema_requires_a_choice_without_teaching_which(self):
        self.assertEqual(CAPTURE_SCHEMA['properties']['action']['enum'],['write','leave'])
        self.assertEqual(set(CAPTURE_SCHEMA['required']),{'action','handoff','note'})
        self.assertNotIn('write or leave',capture_prompt(self.fixtures[0]))
        self.assertNotIn('decision_fidelity',json.dumps(CAPTURE_SCHEMA))

    def test_incomplete_provider_output_is_retained_and_fails(self):
        config={'max_calls':1,'max_generated_tokens':100,'max_seconds':5,'max_tokens':50,'judge_max_tokens':50,
                'model':'test-model','judge':'test-judge','rates':{'evaluated':[.4,1.6],'judge':[1,5]},'budget_usd':5}
        result={'model':'test-model','text':'partial','input_tokens':3,'output_tokens':2,'complete':False,'requested_model_match':True}
        with tempfile.TemporaryDirectory() as t,patch.object(run,'call',return_value=result):
            p=Path(t)/'call.json'
            with self.assertRaises(ProviderError):run.Budget(config).invoke('evaluated','system','user',p)
            receipt=json.loads(p.read_text())
            self.assertEqual(receipt['result']['text'],'partial')
            self.assertIsNotNone(receipt['nominal_usd'])
            self.assertIn('incomplete',receipt['error'])

    def test_invalid_judge_output_does_not_become_a_result(self):
        j=good_judgment();j['resume_correct']='yes'
        with self.assertRaises(ValueError):validate_judgment(j)

    def test_source_tagged_quote_cannot_quote_input_or_paraphrase(self):
        fields={'capture_note':'Leave this handoff unchanged.'}
        j=good_judgment();j['evidence_quotes']=[{'source':'capture_note','quote':'Leave this handoff unchanged.'}]
        self.assertEqual(validate_evidence(j,fields),j)
        j['evidence_quotes']=[{'source':'capture_note','quote':'Capture output: Leave this handoff unchanged.'}]
        with self.assertRaises(ValueError):validate_evidence(j,fields)
        j['evidence_quotes']=[{'source':'expected','quote':'Leave this handoff unchanged.'}]
        with self.assertRaises(ValueError):validate_evidence(j,fields)

    def test_critical_failure_cannot_have_all_passing_criteria(self):
        j=good_judgment();j['critical_failure']=True
        with self.assertRaises(ValueError):validate_judgment(j)

    def test_old_extra_rationale_json_is_not_coerced_into_a_result(self):
        with self.assertRaises(ValueError):parse_json('```json\n'+json.dumps(good_judgment())+'\n```\nAdditional rationale')
        j=good_judgment();j['evidence_quotes']=[]
        with self.assertRaises(ValueError):validate_judgment(j)

    def test_empty_write_rejected(self):
        with self.assertRaises(ValueError):validate_capture({'action':'write','handoff':'','note':''})

    def test_paired_interval_clusters_repeats(self):
        ts=[]
        for fixture in ('one','two'):
            for rep in range(2):
                for c in ('skill','baseline'):
                    j=good_judgment();j['resume_correct']=c=='skill'
                    ts.append({'fixture_id':fixture,'condition':c,'repeat':rep,'judgment':j})
        x=paired_difference(ts,'baseline',resamples=100)
        self.assertEqual(x['fixture_pairs'],2)
        self.assertEqual(x['delta_resume'],1)
        self.assertEqual(x['ci95'],[1,1])

    def test_redirect_refused_before_forwarding_auth(self):
        with self.assertRaises(ProviderError):NoRedirect().redirect_request(None,None,302,'Moved',{},'https://elsewhere.invalid')

    def test_offline_never_claims_behavior_and_exact_resume_only(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()), patch.object(run,'call',side_effect=AssertionError('No provider calls allowed')):
            args=['--offline-smoke','--run-id','test','--output-root',temp,'--date','2026-10-28']
            self.assertEqual(run.main(args),0)
            p=Path(temp)/'2026-10-28/test'
            s=json.loads((p/'summary.json').read_text())
            self.assertIsNone(s['metrics_by_condition'])
            self.assertIsNone(s['paired_comparisons'])
            self.assertEqual(s['provider_calls'],0)
            before=(p/'manifest.json').read_bytes()
            self.assertEqual(run.main(args+['--resume']),0)
            self.assertEqual(before,(p/'manifest.json').read_bytes())
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                run.main(args+['--resume','--max-tokens','1500'])

    def test_budget_prevents_first_call_when_cap_insufficient(self):
        config={'max_calls':1,'max_generated_tokens':100,'max_seconds':5,'max_tokens':50,'judge_max_tokens':50,
                'model':'test-model','judge':'test-judge','rates':{'evaluated':[100,100],'judge':[100,100]},'budget_usd':.00001}
        b=run.Budget(config)
        with tempfile.TemporaryDirectory() as t,patch.object(run,'call',side_effect=AssertionError('Should not call')):
            with self.assertRaises(run.BudgetExceeded):b.invoke('evaluated','hello','world',Path(t)/'call.json')
        self.assertEqual(b.calls,0)

    def test_read_only_virtual_packet_is_not_mutated(self):
        f=copy.deepcopy(next(f for f in self.fixtures if f['id']=='f08'))
        key=json.loads((ROOT/'evals/key.json').read_text())[f['id']]
        class FakeBudget:
            count=0
            def invoke(self,role,system,user,path,response_schema=None):
                self.count+=1
                if self.count==1:return json.dumps({'action':'write','handoff':'UNAUTHORIZED REPLACEMENT','note':''})
                if self.count==2:return json.dumps({'next_action':'Report missing provenance.','rationale':'Read-only task.','actions':[],'verification':'Not checked.'})
                j=good_judgment();j['evidence_quotes']=[{'source':'resume_next_action','quote':'Report missing provenance.'}];return json.dumps(j)
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            result=run.run_trial(f,'baseline',0,'masked',{},'','',key,p,FakeBudget())
            self.assertTrue(result['unauthorized_write'])
            self.assertEqual((p/'raw/masked/workspace/HANDOFF.md').read_text(),f['existing_handoff'])
            self.assertTrue(score_trial(result)['critical_failure'])


if __name__=='__main__':unittest.main()
