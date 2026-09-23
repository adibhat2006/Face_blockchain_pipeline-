import os
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables from .env file
load_dotenv()

# Read Web3 configuration from environment variables
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("WEB3_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# ABI including both recordVerification and getRecord functions
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "imageHash", "type": "string"},
            {"internalType": "uint256", "name": "matchCount", "type": "uint256"},
            {"internalType": "uint256", "name": "topScore", "type": "uint256"}
        ],
        "name": "recordVerification",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "imageHash", "type": "string"}
        ],
        "name": "getRecord",
        "outputs": [
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "uint256", "name": "matchCount", "type": "uint256"},
            {"internalType": "uint256", "name": "topScore", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def get_web3_instance():
    return Web3(Web3.HTTPProvider(RPC_URL))

def get_contract(w3):
    checksum_contract_addr = Web3.to_checksum_address(CONTRACT_ADDRESS)
    return w3.eth.contract(address=checksum_contract_addr, abi=CONTRACT_ABI)

def record_verification_on_chain(image_hash: str, match_count: int = 0, top_score: int = 0):
    """
    Submits a signed transaction to the FaceChain contract on-chain.
    """
    if not PRIVATE_KEY or not CONTRACT_ADDRESS:
        raise ValueError("Missing WEB3_PRIVATE_KEY or CONTRACT_ADDRESS in environment variables.")

    w3 = get_web3_instance()
    if not w3.is_connected():
        raise ConnectionError(f"Unable to connect to blockchain node at {RPC_URL}")

    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = get_contract(w3)
    nonce = w3.eth.get_transaction_count(account.address)

    # Build transaction dictionary
    transaction = contract.functions.recordVerification(
        image_hash,
        int(match_count),
        int(top_score)
    ).build_transaction({
        'chainId': 31337,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
        'from': account.address
    })

    # Sign transaction locally using private key
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)

    # Web3.py v6 compatibility
    raw_tx = getattr(signed_tx, "raw_transaction", getattr(signed_tx, "rawTransaction", None))
    tx_hash = w3.eth.send_raw_transaction(raw_tx)
    tx_hash_hex = w3.to_hex(tx_hash)

    # Wait for receipt with timeout and status validation
    try:
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        status = tx_receipt.get("status") if hasattr(tx_receipt, "get") else getattr(tx_receipt, "status", None)
        if status != 1:
            raise RuntimeError(f"Transaction reverted on-chain: {tx_hash_hex}")
    except Exception as e:
        raise TimeoutError(f"Web3 transaction receipt timed out or failed: {str(e)}")

    block_num = tx_receipt.get("blockNumber") if hasattr(tx_receipt, "get") else getattr(tx_receipt, "blockNumber", 0)

    return {
        "transaction_hash": tx_hash_hex,
        "block_number": block_num
    }

def verify_face_record(image_hash: str):
    """
    Verifies if a given image hash exists in the smart contract ledger.
    """
    if not CONTRACT_ADDRESS:
        return {"verified": False, "error": "Missing CONTRACT_ADDRESS"}

    w3 = get_web3_instance()
    if not w3.is_connected():
        return {"verified": False, "error": "Blockchain node unreachable"}

    try:
        contract = get_contract(w3)
        record = contract.functions.getRecord(image_hash).call()
        return {
            "verified": record[0] != 0,
            "timestamp": record[0],
            "match_count": record[1],
            "top_score": record[2]
        }
    except Exception as e:
        return {"verified": False, "error": str(e)}