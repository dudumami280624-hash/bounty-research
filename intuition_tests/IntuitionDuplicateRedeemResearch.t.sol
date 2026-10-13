// SPDX-License-Identifier: BUSL-1.1
// Research-only regression on the official pinned Intuition V2 source.
// Do not classify a failing assertion as a bounty vulnerability without impact review.
pragma solidity 0.8.29;

import {BaseTest} from "tests/BaseTest.t.sol";
import {MultiVault} from "src/protocol/MultiVault.sol";

contract IntuitionDuplicateRedeemResearch is BaseTest {
    uint256 internal curveId;

    function setUp() public override {
        super.setUp();
        curveId = getDefaultCurveId();
    }

    function _seed() internal returns (bytes32 termId, uint256 depositedShares) {
        termId = createSimpleAtom("Intuition duplicate redemption invariant", ATOM_COST[0], users.alice);
        depositedShares = makeDeposit(users.alice, users.alice, termId, curveId, 20e18, 1e4);
        assertGt(depositedShares, 0, "control: deposit must mint shares");
    }

    // Paired positive control: duplicate term in a batch vs two independent redemptions
    // on precisely the same snapshot, with the same shares and receiver.
    function testFuzz_DuplicateTermBatchMatchesSequential(uint16 firstBps, uint16 secondBps) public {
        (bytes32 termId, uint256 totalShares) = _seed();
        uint256 first = totalShares * bound(uint256(firstBps), 100, 2000) / 10_000;
        uint256 second = totalShares * bound(uint256(secondBps), 100, 2000) / 10_000;
        assertGt(first, 0);
        assertGt(second, 0);
        uint256 snapshot = vm.snapshotState();

        uint256 startBalance = users.alice.balance;
        uint256 firstAssets = redeemShares(users.alice, users.alice, termId, curveId, first, 0);
        uint256 secondAssets = redeemShares(users.alice, users.alice, termId, curveId, second, 0);
        uint256 sequentialReceived = users.alice.balance - startBalance;
        uint256 sequentialShares = protocol.multiVault.getShares(users.alice, termId, curveId);
        uint256 sequentialVaultBalance = address(protocol.multiVault).balance;
        assertEq(sequentialReceived, firstAssets + secondAssets, "control: sequential payout");
        assertTrue(vm.revertToState(snapshot), "snapshot restore failed");

        bytes32[] memory terms = new bytes32[](2);
        terms[0] = termId;
        terms[1] = termId;
        uint256[] memory curves = new uint256[](2);
        curves[0] = curveId;
        curves[1] = curveId;
        uint256[] memory shares = new uint256[](2);
        shares[0] = first;
        shares[1] = second;
        uint256[] memory minAssets = new uint256[](2);

        uint256[] memory payouts =
            redeemSharesBatch(users.alice, users.alice, terms, curves, shares, minAssets);
        assertEq(payouts.length, 2);
        assertEq(payouts[0] + payouts[1], sequentialReceived, "batch must not increase user payout");
        assertEq(users.alice.balance - startBalance, sequentialReceived, "balance conservation");
        assertEq(protocol.multiVault.getShares(users.alice, termId, curveId), sequentialShares, "share conservation");
        assertEq(address(protocol.multiVault).balance, sequentialVaultBalance, "vault balance conservation");
    }

    // Negative control: repeated term must not allow spending more than available shares.
    function test_DuplicateTermOverdraftRevertsAtomically() public {
        (bytes32 termId, uint256 totalShares) = _seed();
        uint256 beforeBalance = users.alice.balance;
        uint256 beforeVaultBalance = address(protocol.multiVault).balance;
        bytes32[] memory terms = new bytes32[](2);
        terms[0] = termId;
        terms[1] = termId;
        uint256[] memory curves = new uint256[](2);
        curves[0] = curveId;
        curves[1] = curveId;
        uint256[] memory shares = new uint256[](2);
        shares[0] = totalShares * 7 / 10;
        shares[1] = totalShares * 7 / 10;
        uint256[] memory minAssets = new uint256[](2);

        resetPrank(users.alice);
        vm.expectRevert(MultiVault.MultiVault_InsufficientSharesInVault.selector);
        protocol.multiVault.redeemBatch(users.alice, terms, curves, shares, minAssets);
        assertEq(users.alice.balance, beforeBalance, "failed batch must not pay out");
        assertEq(address(protocol.multiVault).balance, beforeVaultBalance, "failed batch must not move vault funds");
        assertEq(protocol.multiVault.getShares(users.alice, termId, curveId), totalShares, "failed batch must not burn");
    }
}
