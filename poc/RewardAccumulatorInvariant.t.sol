// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity 0.8.28;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {RewardAccumulator} from "../src/RewardAccumulator.sol";
import {Staker} from "../src/Staker.sol";

// The deployed ZEN implementation is not assumed to support token callbacks.
// This harness tests genuine RewardAccumulator code with a standard ERC20.
contract EchidnaPlainToken is ERC20 {
    constructor() ERC20("Invariant Test ZEN", "IZEN") {}
    function mint(address to, uint256 n) external { _mint(to, n); }
}

contract EchidnaRewardReceiver {
    uint256 public notified;
    function notifyRewardAmount(uint256 n) external { notified += n; }
}

contract RewardAccumulatorInvariant {
    EchidnaPlainToken public token;
    EchidnaRewardReceiver public receiver;
    RewardAccumulator public accumulator;
    uint256 public funded;
    uint256 public donated;

    constructor() {
        token = new EchidnaPlainToken();
        receiver = new EchidnaRewardReceiver();
        accumulator = new RewardAccumulator(Staker(address(receiver)), token, 1, false);
        token.approve(address(accumulator), type(uint256).max);
    }

    function fund(uint96 raw) external {
        uint256 n = uint256(raw);
        token.mint(address(this), n);
        accumulator.transferAndNotifyRewards(n);
        funded += n;
    }

    function donate(uint96 raw) external {
        uint256 n = uint256(raw);
        token.mint(address(accumulator), n);
        donated += n;
    }

    function accountDonation(uint96 raw) external {
        uint256 n = uint256(raw);
        // The real contract checks the available unaccounted token balance.
        accumulator.notifyAlreadyTransferredRewards(n);
    }

    function forwardRewards() external {
        accumulator.sendRewardsToStaker();
    }

    // Echidna mutates call sequences, caller inputs and timestamps.
    // These properties apply to *standard* ERC20 only, not a malicious callback token.
    function echidna_recorded_rewards_have_token_backing() external view returns (bool) {
        return token.balanceOf(address(accumulator)) >= accumulator.accumulatedRewards();
    }

    function echidna_no_fabricated_reward_notifications() external view returns (bool) {
        return token.balanceOf(address(receiver)) == receiver.notified();
    }

    function echidna_no_rewards_from_thin_air() external view returns (bool) {
        return receiver.notified() <= funded + donated;
    }
}
