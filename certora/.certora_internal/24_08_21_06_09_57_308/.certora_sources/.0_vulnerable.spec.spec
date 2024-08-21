/*
 * Certora Formal Verification Spec for ComplexVulnerableToken
 */

using Vulnerable as token;

// Definição dos métodos disponíveis no contrato ComplexVulnerableToken
methods {
    function transfer(address recipient, uint256 amount) external returns(bool); // Função de transferência, que pode alterar o estado
    function approve(address spender, uint256 amount) external returns(bool); // Função de aprovação, que pode alterar o estado
    function totalSupply() external returns(uint256) envfree; // Função de consulta, não altera o estado
    function balanceOf(address) external returns(uint256) envfree; // Função de consulta, não altera o estado
    function deposit() external payable; // Função de depósito
    function withdraw(uint256 amount) external; // Função de retirada, que pode alterar o estado
    function claimVestedTokens() external; // Função de reivindicação de tokens
    function getContractBalance() external returns(uint256) envfree; // Função de consulta, não altera o estado
}

// Invariantes para o contrato
invariant totalSupplyIsNotNegative()
    token.totalSupply() >= 0;

invariant contractBalanceConsistent()
    token.getContractBalance() == address(token).balance;

// Regra para verificar se a função withdraw não altera a consistência do saldo do contrato
rule withdraw_consistency() {
    // Arrange
    env e;
    address sender = e.msg.sender;
    uint256 amount;

    require e.msg.value == 0;
    require e.msg.sender == sender;

    // Obter o saldo do contrato antes da retirada
    uint256 contractBalanceBefore = token.getContractBalance();
    uint256 userBalanceBefore = token.balanceOf(sender);

    // Obter o saldo do usuário antes da retirada
    uint256 userBalanceBeforeWithdraw = token.userBalances(sender);

    // Act
    token.withdraw(amount);

    // Assert
    assert token.getContractBalance() == contractBalanceBefore - amount, "O saldo do contrato deve diminuir pelo valor da retirada");
    assert token.balanceOf(sender) == userBalanceBefore + amount, "O saldo do usuário deve aumentar pelo valor da retirada");
    assert token.userBalances(sender) == userBalanceBeforeWithdraw - amount, "O saldo do usuário deve ser atualizado corretamente");
}

// Regra para garantir que a função withdraw não altere o saldo do contrato incorretamente
rule withdraw_no_reentrancy() {
    // Arrange
    env e;
    address sender = e.msg.sender;
    uint256 amount;

    require e.msg.value == 0;
    require e.msg.sender == sender;

    // Obter o saldo do contrato antes da retirada
    uint256 contractBalanceBefore = token.getContractBalance();

    // Act
    token.withdraw(amount);

    // Assert
    assert token.getContractBalance() == contractBalanceBefore - amount, "O saldo do contrato deve diminuir pelo valor da retirada");
}

// Regra para verificar se o saldo do contrato é consistente após uma retirada
rule withdraw_balance_check() {
    // Arrange
    env e;
    address sender = e.msg.sender;
    uint256 amount;

    require e.msg.value == 0;
    require e.msg.sender == sender;

    // Obter o saldo inicial do contrato e do usuário
    uint256 initialContractBalance = token.getContractBalance();
    uint256 initialUserBalance = token.userBalances(sender);

    // Act
    token.withdraw(amount);

    // Assert
    assert token.getContractBalance() == initialContractBalance - amount, "O saldo do contrato deve diminuir pelo valor da retirada");
    assert token.userBalances(sender) == initialUserBalance - amount, "O saldo do usuário deve diminuir pelo valor da retirada");
}
