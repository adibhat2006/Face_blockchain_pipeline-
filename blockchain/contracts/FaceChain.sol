// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract FaceChain {
    struct VerificationRecord {
        bytes32 imageHash;
        uint256 timestamp;
        address submittedBy;
        bool exists;
    }

    mapping(bytes32 => VerificationRecord) private records;

    event FaceRecordCreated(
        bytes32 indexed imageHash,
        uint256 timestamp,
        address indexed submittedBy
    );

    function storeFaceRecord(bytes32 imageHash) external {
        require(imageHash != bytes32(0), "Invalid image hash");
        require(!records[imageHash].exists, "Record already exists");

        records[imageHash] = VerificationRecord({
            imageHash: imageHash,
            timestamp: block.timestamp,
            submittedBy: msg.sender,
            exists: true
        });

        emit FaceRecordCreated(imageHash, block.timestamp, msg.sender);
    }

    function verifyFaceRecord(bytes32 imageHash)
        external
        view
        returns (bool verified, uint256 timestamp, address submittedBy)
    {
        VerificationRecord memory record = records[imageHash];
        return (record.exists, record.timestamp, record.submittedBy);
    }
}