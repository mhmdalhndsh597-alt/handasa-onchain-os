import unittest
import os
from decimal import Decimal
from unittest.mock import patch

from asset_consolidator import consolidate
from system_guard import check_rpc, main as system_guard_main


class OnchainOSTests(unittest.TestCase):
    @patch("asset_consolidator.rpc_call")
    def test_consolidates_observed_native_balances(self, rpc_call):
        rpc_call.side_effect = ["0x10", "0xde0b6b3a7640000"]
        report = consolidate("https://rpc.example", ["0x" + "1" * 40], {"ETH": Decimal("2000")}, "ETH")
        self.assertEqual(report["block"], 16)
        self.assertEqual(report["total_value_usd"], "2000")
        self.assertFalse(report["ownership_verified"])
        self.assertFalse(report["transaction_signing"])

    @patch("system_guard.rpc_call", return_value="0x10")
    def test_health_check_is_read_only(self, rpc_call):
        result = check_rpc("https://rpc.example")
        self.assertEqual(result["status"], "ok")
        rpc_call.assert_called_once_with("https://rpc.example", "eth_blockNumber", [])

    @patch("system_guard.check_rpc", return_value={"endpoint": "rpc.example", "status": "ok"})
    def test_empty_rpc_urls_falls_back_to_single_url(self, check_rpc_mock):
        with patch.dict(os.environ, {"NETWORK_RPC_URLS": "", "NETWORK_RPC_URL": "https://rpc.example"}):
            self.assertEqual(system_guard_main(), 0)
        check_rpc_mock.assert_called_once_with("https://rpc.example")

    @patch("system_guard.check_rpc", return_value={"endpoint": "rpc.example", "status": "ok"})
    def test_blank_rpc_urls_falls_back_to_single_url(self, check_rpc_mock):
        with patch.dict(os.environ, {"NETWORK_RPC_URLS": " , ", "NETWORK_RPC_URL": "https://rpc.example"}):
            self.assertEqual(system_guard_main(), 0)
        check_rpc_mock.assert_called_once_with("https://rpc.example")

    def test_no_transaction_submission_in_source(self):
        for filename in ("asset_consolidator.py", "system_guard.py"):
            with open(filename, encoding="utf-8") as handle:
                source = handle.read()
            self.assertNotIn("eth_sendRawTransaction", source)
            self.assertNotIn("private_key", source.lower())


if __name__ == "__main__":
    unittest.main()
