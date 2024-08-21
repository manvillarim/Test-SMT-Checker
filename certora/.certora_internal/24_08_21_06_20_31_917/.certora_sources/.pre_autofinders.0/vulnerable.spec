/*
 * Certora Formal Verification Spec for ComplexVulnerableToken
 */

using Vulnerable as token;

methods {
    function transfer(address recipient, uint256 amount) external returns(bool);
    function approve(address spender, uint256 amount) external returns(bool);
    function totalSupply() external returns(uint256) envfree;
    function balanceOf(address) external returns(uint256);
    //function deposit() external payable;
    function withdraw(uint256 amount) external;
    function claimVestedTokens() external;
    function getContractBalance() external returns(uint256) envfree;
}

invariant totalSupplyIsNotNegative()
    token.totalSupply() >= 0;

invariant contractBalanceConsistent()
    token.getContractBalance() == address(token).balance;

rule withdraw_consistency() {
    env e;
    address sender = e.msg.sender;
    uint256 amount;

    require e.msg.value == 0;
    require e.msg.sender == sender;

    uint256 contractBalanceBefore = token.getContractBalance();
    uint256 userBalanceBefore = token.balanceOf(sender);

    token.withdraw(amount);

    assert token.getContractBalance() == to_mathint(contractBalanceBefore - amount);
    assert token.balanceOf(sender) == to_mathint(userBalanceBefore + amount);
}

rule withdraw_no_reentrancy() {
    env e;
    address sender = e.msg.sender;
    uint256 amount;

    require e.msg.value == 0;
    require e.msg.sender == sender;

    uint256 contractBalanceBefore = token.getContractBalance();

    token.withdraw(amount);

    assert token.getContractBalance() == to_mathint(contractBalanceBefore - amount);
}

rule withdraw_balance_check() {
    env e;
    address sender = e.msg.sender;
    uint256 amount;

    require e.msg.value == 0;
    require e.msg.sender == sender;

    uint256 initialContractBalance = token.getContractBalance();
    uint256 initialUserBalance = token.balanceOf(sender);

    token.withdraw(amount);

    assert token.getContractBalance() == assert_uint256(initialContractBalance - amount);
    assert token.balanceOf(sender) == assert_uint256(initialUserBalance - amount);
}
