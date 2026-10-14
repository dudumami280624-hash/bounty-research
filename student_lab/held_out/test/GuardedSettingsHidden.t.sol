// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/GuardedSettings.sol";

contract UnprivilegedCaller {
    function attemptUpdate(GuardedSettings s, uint256 n) external returns (bool) {
        try s.updateLimit(n) { return true; } catch { return false; }
    }
    function attemptTransfer(GuardedSettings s, address a) external returns (bool) {
        try s.transferAdmin(a) { return true; } catch { return false; }
    }
}

contract GuardedSettingsHiddenTest {
    function testAdminCanUpdateLimit() public {
        GuardedSettings s = new GuardedSettings();
        s.updateLimit(123);
        require(s.limit() == 123, "admin update failed");
    }
    function testStrangerCannotUpdateLimit() public {
        GuardedSettings s = new GuardedSettings();
        UnprivilegedCaller stranger = new UnprivilegedCaller();
        require(!stranger.attemptUpdate(s, 999), "stranger updated limit");
        require(s.limit() == 0, "limit was changed");
    }
    function testStrangerCannotSeizeAdmin() public {
        GuardedSettings s = new GuardedSettings();
        UnprivilegedCaller stranger = new UnprivilegedCaller();
        require(!stranger.attemptTransfer(s, address(stranger)), "stranger seized admin");
        require(s.admin() == address(this), "admin changed");
    }
    function testCannotRenounceToZero() public {
        GuardedSettings s = new GuardedSettings();
        try s.transferAdmin(address(0)) { revert("zero admin accepted"); } catch Error(string memory reason) {
            require(keccak256(bytes(reason)) != keccak256(bytes("zero admin accepted")), "accepted zero admin");
        } catch {}
        require(s.admin() == address(this), "admin renounced");
    }
    function testTransferredAdminCanUpdate() public {
        GuardedSettings s = new GuardedSettings();
        UnprivilegedCaller newAdmin = new UnprivilegedCaller();
        s.transferAdmin(address(newAdmin));
        require(newAdmin.attemptUpdate(s, 456), "new admin rejected");
        require(s.limit() == 456, "new admin update missing");
    }
}
