#!/usr/bin/env python3
"""Behavioral regression tests for the v65 dead-frame candidate scanner."""
import importlib.util
import unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"scripts"/"hold_audit_v65.py"
spec=importlib.util.spec_from_file_location("hold_audit_v65",p)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestHolds(unittest.TestCase):
    def test_long_static_detected(self):
        spans=module.detect([.1]*16+[25]*2,[0]*16+[.4]*2,10,max_hold=.85)
        self.assertEqual(spans[0]["duration"],1.6)
    def test_short_hold_not_flagged(self):
        self.assertFalse(module.detect([.1]*6+[25]+[.1]*7,[0]*6+[.4]+[0]*7,10,max_hold=.85))
    def test_actual_motion_not_flagged(self):
        self.assertFalse(module.detect([3.]*25,[.1]*25,10))
    def test_specific_hold_reason(self):
        spans=[{"start":22.,"end":23.2,"duration":1.2}]
        module.apply_allowlist(spans,{"holds":[{"start":21.9,"end":23.3,"reason":"deliberate brand card reading after the spoken URL"}]})
        self.assertTrue(spans[0]["approved_hold"])
    def test_invalid_reason_rejected(self):
        with self.assertRaises(ValueError):
            module.apply_allowlist([{"start":0,"end":1}],{"holds":[{"start":0,"end":1,"reason":"fine"}]})

if __name__=="__main__":unittest.main()
