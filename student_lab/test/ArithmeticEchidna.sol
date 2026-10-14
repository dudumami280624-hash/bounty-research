// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/RewardMath.sol";
contract ArithmeticEchidna {
    RewardMath private immutable math;
    constructor() { math = new RewardMath(); }
    function echidna_proportional_bounded() public view returns (bool) {
        uint256 amount = 1000000;
        uint256 numerator = 3;
        uint256 denominator = 7;
        return math.proportional(amount, numerator, denominator) <= amount;
    }
}
