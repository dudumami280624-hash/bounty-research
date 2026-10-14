// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/RewardMath.sol";

// Actual stateful Echidna property with fuzzed transaction arguments.
// uint96 x uint96 multiplication fits uint192, so valid inputs cannot overflow.
contract ArithmeticEchidna {
    RewardMath private immutable math;
    bool private bounded = true;
    uint256 public validCases;

    constructor() { math = new RewardMath(); }

    function checkBounded(uint96 amount, uint96 numerator, uint96 denominator) public {
        if (denominator == 0 || numerator > denominator) return;
        uint256 result = math.proportional(uint256(amount), uint256(numerator), uint256(denominator));
        if (result > uint256(amount)) bounded = false;
        validCases++;
    }

    function echidna_proportional_bounded() public view returns (bool) {
        return bounded;
    }
}
