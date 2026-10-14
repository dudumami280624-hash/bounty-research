// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RoleSettings {
    address public owner;
    uint256 public setting;
    constructor() { owner = msg.sender; }
    function update(uint256 value) external {
        require(msg.sender == owner, "owner only");
        setting = value;
    }
}
