// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {RewardAccumulator} from "../src/RewardAccumulator.sol";
import {Staker} from "../src/Staker.sol";

contract SecurityRewardToken is ERC20 {
    constructor() ERC20("Reward", "RWD") {}
    function mint(address to, uint256 amount) external { _mint(to, amount); }
}

contract RejectRewardNotification {
    function notifyRewardAmount(uint256) external pure { revert("notification rejected"); }
}

contract RewardAccumulatorSecurityTest is Test {
    SecurityRewardToken token;
    RewardAccumulator accumulator;
    RejectRewardNotification rejector;
    address contributor = address(0xBEEF);

    function setUp() public {
        token = new SecurityRewardToken();
        rejector = new RejectRewardNotification();
        accumulator = new RewardAccumulator(Staker(address(rejector)), token, 1 days, false);
        token.mint(contributor, 100 ether);
        vm.prank(contributor);
        token.approve(address(accumulator), type(uint256).max);
    }

    // Failed downstream notification must atomically roll back the token transfer.
    function testFuzz_rejectedNotificationCannotLoseRewards(uint96 rawAmount) public {
        uint256 amount = bound(uint256(rawAmount), 1, 100 ether);
        vm.prank(contributor);
        accumulator.transferAndNotifyRewards(amount);
        uint256 beforeBalance = token.balanceOf(address(accumulator));
        uint256 beforeAccounted = accumulator.accumulatedRewards();
        vm.warp(block.timestamp + 1 days);
        vm.expectRevert(bytes("notification rejected"));
        accumulator.sendRewardsToStaker();
        assertEq(token.balanceOf(address(accumulator)), beforeBalance);
        assertEq(accumulator.accumulatedRewards(), beforeAccounted);
        assertEq(token.balanceOf(address(rejector)), 0);
    }

    function test_unwhitelistedCannotRecordRewards() public {
        accumulator.setWhitelistEnabled(true);
        vm.prank(contributor);
        vm.expectRevert(RewardAccumulator.NotWhitelisted.selector);
        accumulator.transferAndNotifyRewards(1 ether);
        assertEq(accumulator.accumulatedRewards(), 0);
        assertEq(token.balanceOf(address(accumulator)), 0);
    }

    function testFuzz_windowCannotBeBypassed(uint32 secondsEarly) public {
        uint256 delta = bound(uint256(secondsEarly), 0, 1 days - 1);
        uint256 next = accumulator.nextRewardTime();
        vm.warp(next - 1 days + delta);
        vm.expectRevert(abi.encodeWithSelector(RewardAccumulator.WaitForNextRewardTime.selector, next));
        accumulator.sendRewardsToStaker();
    }
}
