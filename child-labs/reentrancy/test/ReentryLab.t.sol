// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import {Test} from "forge-std/Test.sol";
import {VulnerableVault,GuardedVault,ReentryProbe} from "../src/ReentryLab.sol";
contract ReentryLabTest is Test {
    VulnerableVault v;
    GuardedVault g;
    ReentryProbe p;
    function setUp() public {
        v = new VulnerableVault();
        g = new GuardedVault();
        p = new ReentryProbe(v,g);
        vm.deal(address(this), 10 ether);
    }
    function testVulnerableReentryDrainsExtraFunds() public {
        v.deposit{value: 3 ether}();
        p.fundVulnerable{value: 1 ether}();
        uint256 beforeBalance = address(p).balance;
        p.attackVulnerable();
        assertEq(address(p).balance - beforeBalance, 2 ether, "reentrancy must drain two withdrawals");
        assertEq(address(v).balance, 2 ether);
        assertEq(p.callbacks(), 2);
    }
    function testGuardedReentryCannotDrainExtraFunds() public {
        g.deposit{value: 3 ether}();
        p.fundGuarded{value: 1 ether}();
        uint256 beforeBalance = address(p).balance;
        p.attackGuarded();
        assertEq(address(p).balance - beforeBalance, 1 ether, "guarded vault pays only credited amount");
        assertEq(address(g).balance, 3 ether);
        assertEq(p.callbacks(), 1);
    }
}
