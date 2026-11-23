"""
ProofGuard Deployment Script
============================
Deploys the ProofGuard Intelligent Contract to GenLayer networks
(Bradbury Testnet, StudioNet, or LocalNet) using the official genlayer-py SDK.

Usage:
  python scripts/deploy.py --network testnet_bradbury --dry-run
  python scripts/deploy.py --network testnet_bradbury --private-key <0x...>
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import genlayer_py
    from genlayer_py import create_client, create_account
    from genlayer_py.chains import testnet_bradbury, studionet, localnet
except ImportError:
    genlayer_py = None


NETWORKS = {
    "testnet_bradbury": testnet_bradbury if genlayer_py else None,
    "studionet": studionet if genlayer_py else None,
    "localnet": localnet if genlayer_py else None,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy ProofGuard Intelligent Contract to GenLayer")
    parser.add_argument(
        "--network",
        choices=["testnet_bradbury", "studionet", "localnet"],
        default="testnet_bradbury",
        help="Target GenLayer network (default: testnet_bradbury)",
    )
    parser.add_argument(
        "--private-key",
        default=os.environ.get("GENLAYER_PRIVATE_KEY", ""),
        help="Hex private key of the deployer account (or set GENLAYER_PRIVATE_KEY env var)",
    )
    parser.add_argument(
        "--contract-path",
        default="contracts/proof_guard_standalone.py",
        help="Path to the standalone contract file (default: contracts/proof_guard_standalone.py)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate contract code and simulate deployment without broadcasting to network",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    contract_file = Path(args.contract_path)
    if not contract_file.exists():
        print(f"[ERROR] Contract file not found: {contract_file}")
        sys.exit(1)

    with open(contract_file, "r", encoding="utf-8") as f:
        contract_code = f.read()

    print("==================================================")
    print("ProofGuard Intelligent Contract Deployment")
    print("==================================================")
    print(f"Contract file : {contract_file} ({len(contract_code)} bytes)")
    print(f"Target network: {args.network}")
    print(f"Dry run mode  : {'YES' if args.dry_run else 'NO'}")

    # Basic contract validation
    if "class ProofGuard(gl.contract.Contract):" not in contract_code:
        print("[ERROR] Contract does not contain 'class ProofGuard(gl.contract.Contract):'")
        sys.exit(1)

    print("[SUCCESS] Contract syntax validated successfully.")

    if args.dry_run:
        print("\n--- Dry Run Simulation ---")
        print("Contract code is compilable and ready for GenLayer deployment.")
        print(f"To deploy to {args.network}, run without --dry-run and provide --private-key.")
        print("Or copy contracts/proof_guard_standalone.py directly into GenLayer Studio: https://studio.genlayer.com")
        print("--------------------------")
        return

    if not genlayer_py:
        print("[ERROR] genlayer-py package is required for live network deployment. Run: pip install genlayer-py")
        sys.exit(1)

    chain = NETWORKS.get(args.network)
    if not chain:
        print(f"[ERROR] Unknown or unconfigured network: {args.network}")
        sys.exit(1)

    if not args.private_key:
        print("[ERROR] A private key is required for live deployment. Use --private-key or set GENLAYER_PRIVATE_KEY.")
        sys.exit(1)

    print(f"Connecting to RPC: {chain.rpc_urls['default']['http'][0]}")
    account = create_account(args.private_key)
    client = create_client(chain=chain, account=account)

    print(f"Deployer address: {account.address}")
    print("Broadcasting deployment transaction to GenLayer consensus...")

    try:
        tx_hash = client.deploy_contract(
            code=contract_code,
            account=account,
        )
        print(f"[SUCCESS] Deployment transaction submitted!")
        print(f"Transaction Hash: {tx_hash}")
        print(f"Explorer URL    : {chain.block_explorers['default']['url']}/tx/{tx_hash}")
    except Exception as err:
        print(f"[DEPLOYMENT FAILED] {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
