// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity 0.8.28;

import {Staker} from "../src/Staker.sol";
import {ZenStakerTest} from "../test/ZenStaker.t.sol";

/// @notice New hypothesis: caller-controlled duplicate or foreign deposit IDs
/// must not inflate the in-scope ZenStaker depositor reward summary.
/// Isolated pinned-source tests only. Passing tests DISPROVE this narrow
/// inflation hypothesis under standard ERC20 and IdentityEarningPowerCalculator.
contract ZenStakerSummaryFuzzTest is ZenStakerTest {
    function testFuzz_OwnedIdReturnsRealReward(uint96 rawAmount) public {
        uint256 amount = bound(uint256(rawAmount), 1e18, 1000e18);
        Staker.DepositIdentifier id = _stake(alice, amount, alice);
        _notifyReward(100e18);
        vm.warp(block.timestamp + 7 days);

        Staker.DepositIdentifier[] memory ids = new Staker.DepositIdentifier[](1);
        ids[0] = id;
        (uint256 staked, uint256 power, uint256 rewards) =
            staker.getDepositorFullSummary(alice, ids);
        assertEq(staked, amount, "Owned stake total mismatch");
        assertEq(power, amount, "Owned earning power mismatch");
        assertGt(rewards, 0, "Positive control must accrue rewards");
        assertEq(rewards, staker.unclaimedReward(id), "Single-ID reward mismatch");
    }

    function testFuzz_DuplicateAndForeignIdsDoNotInflateRewards(
        uint96 rawAlice, uint96 rawBob, uint8 rawDuplicates
    ) public {
        uint256 aliceAmount = bound(uint256(rawAlice), 1e18, 1000e18);
        uint256 bobAmount = bound(uint256(rawBob), 1e18, 1000e18);
        uint256 duplicates = bound(uint256(rawDuplicates), 1, 7);
        Staker.DepositIdentifier aliceId = _stake(alice, aliceAmount, alice);
        Staker.DepositIdentifier bobId = _stake(bob, bobAmount, bob);
        _notifyReward(200e18);
        vm.warp(block.timestamp + 7 days);

        Staker.DepositIdentifier[] memory ids =
            new Staker.DepositIdentifier[](duplicates + 2);
        ids[0] = bobId; // Negative control: foreign deposit
        for (uint256 i = 1; i < ids.length; ++i) {
            ids[i] = aliceId; // Negative control: repeated owned deposit
        }
        (uint256 staked, uint256 power, uint256 rewards) =
            staker.getDepositorFullSummary(alice, ids);
        uint256 expected = staker.unclaimedReward(aliceId);
        assertGt(expected, 0, "Test setup must have real accrued rewards");
        assertEq(staked, aliceAmount, "Foreign ID changed principal total");
        assertEq(power, aliceAmount, "Foreign ID changed earning power");
        assertEq(rewards, expected, "Duplicate or foreign ID inflated reward");
    }

    function test_ForeignOnlyIdsYieldNoUnclaimedRewards() public {
        _stake(alice, 10e18, alice);
        Staker.DepositIdentifier bobId = _stake(bob, 10e18, bob);
        _notifyReward(100e18);
        vm.warp(block.timestamp + 7 days);
        Staker.DepositIdentifier[] memory ids = new Staker.DepositIdentifier[](2);
        ids[0] = bobId;
        ids[1] = bobId;
        (uint256 staked, uint256 power, uint256 rewards) =
            staker.getDepositorFullSummary(alice, ids);
        assertEq(staked, 10e18);
        assertEq(power, 10e18);
        assertEq(rewards, 0, "Foreign rewards were counted");
    }

    // Positive regression: separate owned deposits must each contribute once.
    function test_TwoOwnedIdsSumRewards() public {
        Staker.DepositIdentifier first = _stake(alice, 20e18, alice);
        Staker.DepositIdentifier second = _stake(alice, 30e18, alice);
        _notifyReward(100e18);
        vm.warp(block.timestamp + 7 days);
        Staker.DepositIdentifier[] memory ids = new Staker.DepositIdentifier[](2);
        ids[0] = first;
        ids[1] = second;
        (uint256 staked, uint256 power, uint256 rewards) =
            staker.getDepositorFullSummary(alice, ids);
        uint256 expected = staker.unclaimedReward(first) + staker.unclaimedReward(second);
        assertGt(expected, 0, "Positive control must accrue rewards");
        assertEq(staked, 50e18, "Two valid deposits principal mismatch");
        assertEq(power, 50e18, "Two valid deposits power mismatch");
        assertEq(rewards, expected, "Valid deposits not counted exactly once");
    }

    // Negative regression: unknown identifiers and repeated IDs cannot inflate rewards.
    function test_UnknownIdAndDuplicateAreIgnored() public {
        Staker.DepositIdentifier first = _stake(alice, 20e18, alice);
        _notifyReward(100e18);
        vm.warp(block.timestamp + 7 days);
        Staker.DepositIdentifier[] memory ids = new Staker.DepositIdentifier[](4);
        ids[0] = Staker.DepositIdentifier.wrap(type(uint256).max);
        ids[1] = first;
        ids[2] = first;
        ids[3] = Staker.DepositIdentifier.wrap(type(uint256).max);
        (uint256 staked, uint256 power, uint256 rewards) =
            staker.getDepositorFullSummary(alice, ids);
        uint256 expected = staker.unclaimedReward(first);
        assertGt(expected, 0, "Negative control must have a real reward to protect");
        assertEq(staked, 20e18, "Unknown ID changed principal");
        assertEq(power, 20e18, "Unknown ID changed earning power");
        assertEq(rewards, expected, "Unknown or duplicate ID inflated rewards");
    }

}
