// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {ZenStaker} from "src/ZenStaker.sol";
import {RewardAccumulator} from "src/RewardAccumulator.sol";

/// @notice Real deployment on a local fork. Never broadcasts public transactions.
/// @dev Scope: Horizen Testnet chain 2651420; official SECURITY.md addresses.
contract HorizenDeploymentForkTest is Test {
    address constant TOKEN = 0xb06EC4ce262D8dbDc24Fac87479A49A7DC4cFb87;
    address constant STAKER = 0x6BF7CF29a8bcE11Aa62Cf593d165C244fA4d3E31;
    address constant ACCUMULATOR = 0x06f5555fee73EDdc385b6d76FE00DB2D96ccDaE8;
    ZenStaker internal staker = ZenStaker(STAKER);
    RewardAccumulator internal accumulator = RewardAccumulator(ACCUMULATOR);

    function test_RealFork_OfficialContractsHaveRuntimeBytecode() public view {
        assertEq(block.chainid, 2651420, "Not the authorized Horizen Testnet");
        assertGt(TOKEN.code.length, 0, "Official tZEN runtime missing");
        assertGt(STAKER.code.length, 0, "In-scope ZenStaker runtime missing");
        assertGt(ACCUMULATOR.code.length, 0, "In-scope RewardAccumulator runtime missing");
    }

    function test_RealFork_StakeAndRewardShareActualToken() public view {
        assertEq(address(staker.STAKE_TOKEN()), TOKEN, "Unexpected deployed stake token");
        assertEq(address(staker.REWARD_TOKEN()), TOKEN, "Unexpected deployed reward token");
        assertEq(address(accumulator.rewardToken()), TOKEN, "Unexpected accumulator reward token");
        assertEq(address(accumulator.staker()), STAKER, "Accumulator forwards to wrong Staker");
    }

    function test_RealFork_UnknownAccountCannotNotifyReward() public {
        address attacker = address(0xBADDCAFE);
        assertFalse(staker.isRewardNotifier(attacker), "Test account unexpectedly authorized");
        vm.prank(attacker);
        vm.expectRevert();
        staker.notifyRewardAmount(10e18);
    }

    function test_RealFork_RewardWindowCannotBeBypassedEarly() public {
        uint256 due = accumulator.nextRewardTime();
        assertGt(due, 1, "Invalid deployed schedule");
        vm.warp(due - 1); // Change local fork time only; never a public chain transaction.
        vm.expectRevert(abi.encodeWithSelector(
            RewardAccumulator.WaitForNextRewardTime.selector, due
        ));
        accumulator.sendRewardsToStaker();
    }
}
