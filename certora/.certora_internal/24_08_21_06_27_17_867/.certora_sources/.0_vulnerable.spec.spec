/*
 * Certora Formal Verification Spec for Vulnerable
 */

using Vulnerable as token;

// Definindo os métodos disponíveis no contrato Vulnerable
methods {
    function totalSupply() external returns(uint256) envfree;
    function balanceOf(address) external returns(uint256) envfree;
    function deposit() external payable;
    function withdraw(uint256 amount) external;
    function getContractBalance() external returns(uint256) envfree;
}

// Invariantes para o contrato
invariant totalSupplyIsNotNegative()
    token.totalSupply() >= 0;

invariant contractBalanceConsistent()
    token.getContractBalance() == address(token).balance;

// Regra para verificar a vulnerabilidade de reentrância na função withdraw
rule withdraw_reentrancy() {
    // Arrange
    env e;
    address attacker = e.msg.sender;
    uint256 depositAmount = 1 ether;
    uint256 withdrawAmount = 1 ether;

    require e.msg.value == depositAmount;
    require e.msg.sender == attacker;

    // Define o saldo do contrato antes da retirada
    uint256 contractBalanceBefore = token.getContractBalance();

    // Realiza o depósito no contrato Vulnerable
    token.deposit{value: depositAmount}();

    // Realiza a retirada que pode ser feita de maneira reentrante
    token.withdraw(withdrawAmount);

    // Assert
    assert token.getContractBalance() == contractBalanceBefore - withdrawAmount;
}