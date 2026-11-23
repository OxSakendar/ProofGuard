# ProofGuard Deployment Guide

This guide covers deploying the ProofGuard Intelligent Contract using **GenLayer Studio** and the **GenLayer Python SDK (`genlayer-py`)**.

---

## 1. Prerequisites

1. **Python**: Python 3.11+ (Python 3.12 / 3.13 recommended).
2. **GenLayer SDK**:
   ```bash
   pip install genlayer-py pytest
   ```
3. **GenLayer Account**: A funded account on GenLayer Bradbury Testnet (Chain ID `4221`) or local testnet.

---

## 2. Deployment via GenLayer Studio (Recommended for Visual Inspection)

GenLayer Studio provides an interactive web-based IDE for developing and deploying Intelligent Contracts.

1. Open [GenLayer Studio](https://studio.genlayer.com).
2. Click **New Contract** and name it `proof_guard.py`.
3. Copy the entire contents of `contracts/proof_guard_standalone.py` into the editor.
4. Ensure the dependency header at the top is preserved:
   ```python
   # v0.3.0
   # { "Depends": "py-genlayer:9b8kjyda2ycxyq4ea6g4yfpnydxhd52gqba5rb8dw7krkh5mn9p0" }
   ```
5. Click **Deploy**.
6. The contract constructor will execute and record your account address as the contract owner.
7. You can now invoke methods (`submit_claim`, `add_evidence`, `verify_claim`) directly from the Studio interface and watch the multi-validator simulation in real time!

---

## 3. Deployment via Python CLI Script

The project provides an automated deployment script in `scripts/deploy.py`.

### 3.1 Dry Run (Syntax & Simulation Check)
```bash
python scripts/deploy.py --network testnet_bradbury --dry-run
```

### 3.2 Live Testnet Deployment
Set your private key as an environment variable or pass it via flag:

```bash
# Set environment variable
export GENLAYER_PRIVATE_KEY="0xYOUR_PRIVATE_KEY"

# Deploy to GenLayer Bradbury Testnet
python scripts/deploy.py --network testnet_bradbury
```

Or pass via argument:
```bash
python scripts/deploy.py --network testnet_bradbury --private-key "0xYOUR_PRIVATE_KEY"
```

The script will output:
- **Contract Code Size**
- **Target RPC & Chain ID**
- **Deployer Address**
- **Transaction Hash**
- **Explorer Link**: `https://explorer-bradbury.genlayer.com/tx/<tx_hash>`

---

## 4. Post-Deployment Verification Workflow

Once deployed, you can interact with your contract using `genlayer-py`:

```python
from genlayer_py import create_client, create_account
from genlayer_py.chains import testnet_bradbury

account = create_account("0xYOUR_PRIVATE_KEY")
client = create_client(chain=testnet_bradbury, account=account)
contract_address = "0xYOUR_DEPLOYED_CONTRACT_ADDRESS"

# 1. Submit a claim
tx = client.contracts.write_contract(
    address=contract_address,
    function_name="submit_claim",
    args=["AlphaGenome v2 Release", "DeepMind released AlphaGenome v2 on Oct 15, 2026.", "Official announcement confirming release."],
)

# 2. Add an evidence URL
client.contracts.write_contract(
    address=contract_address,
    function_name="add_evidence",
    args=["claim_1", "https://deepmind.google/discover/blog/alphagenome-v2", "a1b2c3d4...64chars", "1.0"],
)

# 3. Trigger decentralized verification
client.contracts.write_contract(
    address=contract_address,
    function_name="verify_claim",
    args=["claim_1"],
)

# 4. Query verified state
claim_data = client.contracts.read_contract(
    address=contract_address,
    function_name="get_claim",
    args=["claim_1"],
)
print("Verified Claim Status:", claim_data["status"])
```
