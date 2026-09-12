import json
import os
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")

CONTRACT_ADDRESS = os.getenv(
    "FACECHAIN_CONTRACT_ADDRESS",
    "0x5FbDB2315678afecb367f032d93F642f64180aa3",
)

# Hardhat's first local account.
# We will load the private key from an environment variable
# instead of hard-coding it into the project.
PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")


# ---------------------------------------------------------
# WEB3 CONNECTION
# ---------------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))


# ---------------------------------------------------------
# LOAD CONTRACT ABI
# ---------------------------------------------------------

ABI_PATH = (
    Path(__file__).resolve().parent.parent
    / "blockchain"
    / "artifacts"
    / "contracts"
    / "FaceChain.sol"
    / "FaceChain.json"
)


def load_abi():
    if not ABI_PATH.exists():
        raise FileNotFoundError(
            f"FaceChain ABI not found at: {ABI_PATH}"
        )

    with open(ABI_PATH, "r", encoding="utf-8") as file:
        artifact = json.load(file)

    return artifact["abi"]


FACECHAIN_ABI = load_abi()


# ---------------------------------------------------------
# CONTRACT INSTANCE
# ---------------------------------------------------------

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=FACECHAIN_ABI,
)


# ---------------------------------------------------------
# CONNECTION CHECK
# ---------------------------------------------------------

def blockchain_status():
    """
    Check whether the local Hardhat blockchain is reachable.
    """

    try:
        connected = w3.is_connected()

        if not connected:
            return {
                "connected": False,
                "message": "Blockchain is not reachable",
            }

        return {
            "connected": True,
            "network_id": w3.eth.chain_id,
            "latest_block": w3.eth.block_number,
            "contract_address": CONTRACT_ADDRESS,
        }

    except Exception as error:
        return {
            "connected": False,
            "message": str(error),
        }


# ---------------------------------------------------------
# STORE FACE RECORD
# ---------------------------------------------------------

def store_face_record(image_hash: str):
    """
    Store a SHA-256 image hash on the FaceChain blockchain.

    image_hash must be a 64-character hexadecimal SHA-256 hash.
    """

    if not w3.is_connected():
        raise RuntimeError(
            "Blockchain is not connected. "
            "Make sure 'npx hardhat node' is running."
        )

    if not PRIVATE_KEY:
        raise RuntimeError(
            "BLOCKCHAIN_PRIVATE_KEY environment variable is not set."
        )

    # Convert SHA-256 hex string into bytes32
    image_hash_bytes = bytes.fromhex(image_hash)

    if len(image_hash_bytes) != 32:
        raise ValueError(
            "Image hash must be a 32-byte SHA-256 hash."
        )

    # Get wallet/account from private key
    account = w3.eth.account.from_key(PRIVATE_KEY)

    # Get current nonce
    nonce = w3.eth.get_transaction_count(account.address)

    # Build transaction
    transaction = contract.functions.storeFaceRecord(
        image_hash_bytes
    ).build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "chainId": w3.eth.chain_id,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        }
    )

    # Sign transaction
    signed_transaction = w3.eth.account.sign_transaction(
        transaction,
        PRIVATE_KEY,
    )

    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    # Wait until blockchain confirms it
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "success": True,
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
        "contract_address": CONTRACT_ADDRESS,
        "submitted_by": account.address,
    }


# ---------------------------------------------------------
# VERIFY FACE RECORD
# ---------------------------------------------------------

def verify_face_record(image_hash: str):
    """
    Check whether an image hash already exists on FaceChain.
    """

    if not w3.is_connected():
        raise RuntimeError(
            "Blockchain is not connected. "
            "Make sure 'npx hardhat node' is running."
        )

    image_hash_bytes = bytes.fromhex(image_hash)

    if len(image_hash_bytes) != 32:
        raise ValueError(
            "Image hash must be a 32-byte SHA-256 hash."
        )

    verified, timestamp, submitted_by = (
        contract.functions.verifyFaceRecord(
            image_hash_bytes
        ).call()
    )

    return {
        "verified": verified,
        "timestamp": timestamp,
        "submitted_by": submitted_by,
        "contract_address": CONTRACT_ADDRESS,
    }