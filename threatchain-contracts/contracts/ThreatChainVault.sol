// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ThreatChainVault {
    // State variable to establish the owner (your Python Backend)
    address public admin;

    // Struct to define what a Threat Log looks like
    struct ThreatLog {
        string threatId;        // A unique hash of the network payload
        uint256 confidence;     // The AI confidence score (multiplied by 10000 for precision)
        string actionTaken;     // "BLOCK" or "REVIEW"
        uint256 timestamp;      // When the attack occurred
    }

    // Array to hold all immutable threat logs
    ThreatLog[] private recordedThreats;

    // Event that broadcasts to your React frontend whenever a new threat is anchored
    event ThreatAnchored(
        string indexed threatId,
        uint256 confidence,
        string actionTaken,
        uint256 timestamp
    );

    // Run once when the contract is deployed
    constructor() {
        admin = msg.sender;
    }

    // Modifier to ensure ONLY your AI backend can log threats
    modifier onlyAdmin() {
        require(msg.sender == admin, "UNAUTHORIZED: Only the ThreatChain AI can log threats.");
        _;
    }

    /**
     * @dev Anchors a verified threat to the blockchain.
     */
    function logThreat(string memory _threatId, uint256 _confidence, string memory _actionTaken) public onlyAdmin {
        
        ThreatLog memory newLog = ThreatLog({
            threatId: _threatId,
            confidence: _confidence,
            actionTaken: _actionTaken,
            timestamp: block.timestamp
        });

        recordedThreats.push(newLog);

        // Emit the event so the frontend UI can update in real-time
        emit ThreatAnchored(_threatId, _confidence, _actionTaken, block.timestamp);
    }

    /**
     * @dev Retrieves all stored threat logs. 
     * Useful for displaying the immutable history on your dashboard.
     */
    function getAllThreats() public view returns (ThreatLog[] memory) {
        return recordedThreats;
    }

    /**
     * @dev Returns the total number of intercepted threats.
     */
    function getTotalThreatCount() public view returns (uint256) {
        return recordedThreats.length;
    }
}