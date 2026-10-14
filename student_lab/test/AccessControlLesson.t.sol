// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "../contracts/RoleSettings.sol";

contract UntrustedCaller {
    function tryUpdate(RoleSettings settings) external returns (bool) {
        (bool ok,) = address(settings).call(abi.encodeWithSelector(settings.update.selector, 99));
        return ok;
    }
}
contract AccessControlLessonTest {
    function testOwnerCanUpdate() public {
        RoleSettings settings = new RoleSettings();
        settings.update(42);
        require(settings.setting() == 42, "owner update failed");
    }
    function testOtherCallerCannotUpdate() public {
        RoleSettings settings = new RoleSettings();
        UntrustedCaller other = new UntrustedCaller();
        require(!other.tryUpdate(settings), "unauthorized update succeeded");
        require(settings.setting() == 0, "unauthorized state change");
    }
}
