// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract RewardMath {
    function proportional(uint256 amount, uint256 numerator, uint256 denominator) external pure returns (uint256) {
        require(denominator != 0, "zero denominator");
        require(numerator <= denominator, "fraction above one");
        return amount * numerator / denominator;
    }
}
