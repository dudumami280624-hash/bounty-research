// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract VulnerableVault {
    mapping(address => uint256) public balance;
    function deposit() external payable { balance[msg.sender] += msg.value; }
    function withdraw() external {
        uint256 amount = balance[msg.sender];
        require(amount > 0, "empty");
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "send");
        balance[msg.sender] = 0;
    }
}
contract GuardedVault {
    mapping(address => uint256) public balance;
    function deposit() external payable { balance[msg.sender] += msg.value; }
    function withdraw() external {
        uint256 amount = balance[msg.sender];
        require(amount > 0, "empty");
        balance[msg.sender] = 0;
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "send");
    }
}
contract ReentryProbe {
    VulnerableVault public vulnerable;
    GuardedVault public guarded;
    uint256 public callbacks;
    constructor(VulnerableVault v, GuardedVault g) { vulnerable=v; guarded=g; }
    function fundVulnerable() external payable { vulnerable.deposit{value: msg.value}(); }
    function fundGuarded() external payable { guarded.deposit{value: msg.value}(); }
    function attackVulnerable() external { vulnerable.withdraw(); }
    function attackGuarded() external { guarded.withdraw(); }
    receive() external payable {
        callbacks++;
        if (msg.sender == address(vulnerable) && callbacks < 2) vulnerable.withdraw();
        if (msg.sender == address(guarded) && callbacks < 2) {
            (bool ok,) = address(guarded).call(abi.encodeWithSelector(GuardedVault.withdraw.selector));
            require(!ok, "guard failed");
        }
    }
}
