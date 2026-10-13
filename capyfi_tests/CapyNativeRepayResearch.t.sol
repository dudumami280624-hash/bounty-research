// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

// Research only: pinned Capyfi source, local EVM and mocked policy hooks.
// This does not prove deployment/source correspondence or a production exploit.
import "../unit/CapyfiBaseTest.sol";

contract CapyNativeRepayResearch is CapyfiBaseTest {
    function setUp() public override {
        super.setUp();
        vm.prank(admin);
        cEther.mint{value: 10 ether}();
        vm.prank(user1);
        cEther.borrow(2 ether);
    }

    function testFuzz_ExactRepayConservesDebtAndCash(uint96 raw) public {
        uint amount = bound(uint(raw), 1, 2 ether);
        uint debtBefore = cEther.borrowBalanceStored(user1);
        uint cashBefore = address(cEther).balance;
        vm.prank(user1);
        cEther.repayBorrow{value: amount}();
        assertEq(cEther.borrowBalanceStored(user1), debtBefore - amount, "debt decrement mismatch");
        assertEq(address(cEther).balance, cashBefore + amount, "cash increment mismatch");
    }

    function testFuzz_RepayBehalfConservesDebtAndCash(uint96 raw) public {
        uint amount = bound(uint(raw), 1, 2 ether);
        uint debtBefore = cEther.borrowBalanceStored(user1);
        uint cashBefore = address(cEther).balance;
        vm.prank(user2);
        cEther.repayBorrowBehalf{value: amount}(user1);
        assertEq(cEther.borrowBalanceStored(user1), debtBefore - amount, "behalf debt mismatch");
        assertEq(address(cEther).balance, cashBefore + amount, "behalf cash mismatch");
    }

    function test_OverpaymentRevertsAtomically() public {
        uint debtBefore = cEther.borrowBalanceStored(user1);
        uint cashBefore = address(cEther).balance;
        vm.prank(user1);
        vm.expectRevert();
        cEther.repayBorrow{value: debtBefore + 1}();
        assertEq(cEther.borrowBalanceStored(user1), debtBefore, "debt changed on revert");
        assertEq(address(cEther).balance, cashBefore, "cash changed on revert");
    }
}
