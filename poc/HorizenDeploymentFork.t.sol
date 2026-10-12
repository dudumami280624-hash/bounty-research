// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {ZenStaker} from "src/ZenStaker.sol";
import {RewardAccumulator} from "src/RewardAccumulator.sol";
import {Staker} from "src/Staker.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @notice Real deployment on a local fork. Never broadcasts public transactions.
/// @dev Scope: Horizen Testnet chain 2651420; official SECURITY.md addresses.

contract TokenCallbackProbe {
    uint256 public fallbackCalls;
    uint256 public receiveCalls;
    fallback() external { fallbackCalls++; }
    receive() external payable { receiveCalls++; }
}

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
    function test_RealFork_ActualTokenPrincipalCannotBeStolenViaWithdraw() public {
        // Fund only the local Anvil/Foundry fork state; public tZEN balances are NOT changed.
        address alice = address(0xA11CE);
        address attacker = address(0xBADDCAFE);
        uint256 original = 1000e18;
        uint256 amount = 100e18;
        deal(TOKEN, alice, original);
        assertEq(IERC20(TOKEN).balanceOf(alice), original, "Local fork funding failed");

        vm.prank(alice);
        IERC20(TOKEN).approve(STAKER, amount);

        vm.prank(alice);
        Staker.DepositIdentifier depositId = staker.stake(amount, alice);
        assertEq(IERC20(TOKEN).balanceOf(alice), original - amount);

        uint256 ownerBalanceBefore = IERC20(TOKEN).balanceOf(alice);
        uint256 attackerBalanceBefore = IERC20(TOKEN).balanceOf(attacker);
        vm.prank(attacker);
        // The actual deployed contract uses a different error selector than
        // the pinned source. Verify the security property, not an assumed ABI.
        vm.expectRevert();
        staker.withdraw(depositId, amount);
        assertEq(IERC20(TOKEN).balanceOf(alice), ownerBalanceBefore, "Owner funds changed");
        assertEq(IERC20(TOKEN).balanceOf(attacker), attackerBalanceBefore, "Attacker gained ZEN");
        (uint96 depositPrincipal,,,,,) = staker.getDepositInfo(depositId);
        assertEq(uint256(depositPrincipal), amount, "Deposit principal changed");

        vm.prank(alice);
        staker.withdraw(depositId, amount);
        assertEq(IERC20(TOKEN).balanceOf(alice), original, "Principal conservation failed");
        assertEq(IERC20(TOKEN).balanceOf(attacker), 0, "Attacker received ZEN");
    }

    function test_RealFork_ActualTokenTransferDoesNotCallbackReceiver() public {
        // This directly tests the production tZEN runtime on a local fork.
        // RewardAccumulator reentry requires token transfer to synchronously call the receiver.
        TokenCallbackProbe probe = new TokenCallbackProbe();
        address alice = address(0xA11CE);
        uint256 amount = 1e18;
        deal(TOKEN, alice, amount);
        vm.prank(alice);
        bool ok = IERC20(TOKEN).transfer(address(probe), amount);
        assertTrue(ok, "Actual tZEN transfer failed");
        assertEq(probe.fallbackCalls(), 0, "Actual tZEN transfer invoked receiver fallback");
        assertEq(probe.receiveCalls(), 0, "Actual tZEN transfer invoked receiver receive");
        assertEq(IERC20(TOKEN).balanceOf(address(probe)), amount, "Actual tZEN transfer accounting mismatch");
    }

    function test_RealFork_ActualTokenApproveDoesNotCallbackSpender() public {
        // ZenStaker's delegation-surrogate path calls token.approve().
        // A token-side callback would be required for the static reentrancy alert to become concrete.
        TokenCallbackProbe probe = new TokenCallbackProbe();
        address alice = address(0xA11CE);
        vm.prank(alice);
        bool ok = IERC20(TOKEN).approve(address(probe), 1e18);
        assertTrue(ok, "Actual tZEN approve failed");
        assertEq(probe.fallbackCalls(), 0, "Actual tZEN approve invoked spender fallback");
        assertEq(probe.receiveCalls(), 0, "Actual tZEN approve invoked spender receive");
        assertEq(IERC20(TOKEN).allowance(alice, address(probe)), 1e18, "Actual tZEN allowance mismatch");
    }


}
