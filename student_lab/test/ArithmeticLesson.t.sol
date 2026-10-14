// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/RewardMath.sol";
contract ArithmeticLessonTest {
    // Foundry fuzzes the inputs; keep multiplication within uint256 bounds.
    function testFuzzProportionalNeverExceedsAmount(uint256 amount, uint256 numerator, uint256 denominator) public {
        denominator = (denominator % 1000000) + 1;
        numerator = numerator % (denominator + 1);
        amount = amount % (type(uint256).max / (denominator + 1));
        RewardMath math = new RewardMath();
        uint256 result = math.proportional(amount, numerator, denominator);
        require(result <= amount, "fraction increased the amount");
        if (numerator == 0) require(result == 0, "zero numerator not zero");
        if (numerator == denominator) require(result == amount, "full share changed amount");
    }
    function testExactFraction() public {
        RewardMath math = new RewardMath();
        require(math.proportional(100, 1, 4) == 25, "wrong fraction");
    }
    function testRoundingDown() public {
        RewardMath math = new RewardMath();
        require(math.proportional(10, 1, 3) == 3, "wrong rounding");
    }
    function testZeroDenominatorRejected() public {
        RewardMath math = new RewardMath();
        (bool ok,) = address(math).call(abi.encodeWithSelector(math.proportional.selector, 10, 1, 0));
        require(!ok, "division by zero accepted");
    }
    function testOverflowRejected() public {
        RewardMath math = new RewardMath();
        (bool ok,) = address(math).call(abi.encodeWithSelector(math.proportional.selector, type(uint256).max, 2, 3));
        require(!ok, "overflow accepted");
    }
}
