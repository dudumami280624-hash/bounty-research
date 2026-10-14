// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/RewardMath.sol";
contract ArithmeticLessonTest {
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
