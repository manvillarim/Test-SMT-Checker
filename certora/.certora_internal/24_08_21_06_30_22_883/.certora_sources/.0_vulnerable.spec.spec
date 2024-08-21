/*
 * Certora Formal Verification Spec for Vulnerable
 */

using Vulnerable as token;

// Definindo os métodos disponíveis no contrato Vulnerable
methods {
    function totalSupply() external returns(uint256) envfree;
    function balanceOf(address) external returns(uint256) envfree;
    //function deposit() external payable;
    function withdraw(uint256 amount) external;
    function getContractBalance() external returns(uint256) envfree;
}

// Invariantes para o contrato
invariant totalSupplyIsNotNegative()
    token.totalSupply() >= 0;

// Regra para verificar a vulnerabilidade de reentrância na função withdraw
rule withdraw_reentrancy() {
    // Arrange
    env e;
    address attacker = e.msg.sender;
    uint256 depositAmount; // Valor fixo para depósito
    uint256 withdrawAmount; // Valor fixo para retirada

    // Define o saldo do contrato antes do depósito
    uint256 initialContractBalance = token.getContractBalance();
    uint256 initialUserBalance = token.balanceOf(attacker);

    // Realiza o depósito no contrato Vulnerable
    e.call{value: depositAmount}(() => token.deposit());

    // Verifica o saldo após o depósito
    uint256 contractBalanceAfterDeposit = token.getContractBalance();
    uint256 userBalanceAfterDeposit = token.balanceOf(attacker);

    // Realiza a retirada
    e.call(() => token.withdraw(withdrawAmount));

    // Assert
    assert token.getContractBalance() == initialContractBalance - withdrawAmount;
    assert token.balanceOf(attacker) == initialUserBalance + withdrawAmount;
}