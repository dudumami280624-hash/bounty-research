// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity 0.8.28;
import {Test} from "forge-std/Test.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {RewardAccumulator} from "../src/RewardAccumulator.sol";
import {Staker} from "../src/Staker.sol";

contract CallbackRewardToken is ERC20 {
    RewardAccumulator public accumulator;
    address public receiver;
    bool public callbackEnabled;
    bool private entered;
    constructor() ERC20("Mock Callback Token", "MCT") {}
    function configure(RewardAccumulator a, address r, bool enabled) external {
        accumulator = a;
        receiver = r;
        callbackEnabled = enabled;
    }
    function mint(address to, uint256 amount) external { _mint(to, amount); }
    function _update(address from, address to, uint256 value) internal override {
        super._update(from, to, value);
        if (callbackEnabled && !entered && from == address(accumulator)
            && to == receiver && value > 0) {
            entered = true;
            accumulator.sendRewardsToStaker();
            entered = false;
        }
    }
}
contract CallbackStaker {
    uint256 public notifications;
    uint256 public totalNotified;
    function notifyRewardAmount(uint256 amount) external {
        notifications++;
        totalNotified += amount;
    }
}
contract RewardAccumulatorReentryTest is Test {
    CallbackRewardToken token;
    CallbackStaker receiver;
    RewardAccumulator accumulator;
    function setUp() public {
        token = new CallbackRewardToken();
        receiver = new CallbackStaker();
        accumulator = new RewardAccumulator(
            Staker(address(receiver)), token, 1 days, false
        );
        token.configure(accumulator, address(receiver), false);
        token.mint(address(this), 200 ether);
        token.approve(address(accumulator), 100 ether);
        accumulator.transferAndNotifyRewards(100 ether);
        // A separate unaccounted donation models surplus reward-token balance.
        token.transfer(address(accumulator), 100 ether);
        vm.warp(block.timestamp + 1 days);
    }
    function test_Control_NoCallback_SendsOnlyAccountedAmount() public {
        accumulator.sendRewardsToStaker();
        assertEq(token.balanceOf(address(receiver)), 100 ether);
        assertEq(token.balanceOf(address(accumulator)), 100 ether);
        assertEq(receiver.notifications(), 1);
    }
    function test_CallbackWithoutSurplus_RevertsAtomically() public {
        // Remove the unaccounted 100-token donation; callback reentry then
        // cannot execute the second transfer and the whole operation reverts.
        vm.prank(address(accumulator));
        token.transfer(address(0xBEEF), 100 ether);
        token.configure(accumulator, address(receiver), true);
        vm.expectRevert();
        accumulator.sendRewardsToStaker();
        assertEq(receiver.notifications(), 0);
        assertEq(token.balanceOf(address(receiver)), 0);
        assertEq(accumulator.accumulatedRewards(), 100 ether);
    }
    function test_ConditionalMaliciousERC20_CallbackCausesDuplicateSend() public {
        token.configure(accumulator, address(receiver), true);
        accumulator.sendRewardsToStaker();
        assertEq(token.balanceOf(address(receiver)), 200 ether);
        assertEq(token.balanceOf(address(accumulator)), 0);
        assertEq(receiver.notifications(), 2);
        // Conditional synthetic callback, NOT evidence that the actual
        // deployed reward token supports callbacks or that a bounty is earned.
    }
}
