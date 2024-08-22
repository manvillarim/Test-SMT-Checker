Pesquisa - Verificação Formal de Contratos Inteligentes

Objetivo: Demonstrar a funcionalidade do SMT Checker em contratos inteligentes com explosão de dados e comparar sua atuação com outras ferramentas de verificação formal da indústria.
Metodologia

1ª Etapa: Criação de um contrato inteligente com uma vulnerabilidade proposital que o SMT Checker não consiga detectar.

2ª Etapa: Simplificação do código para preservar a semântica e facilitar o trabalho do model-checker.

3ª Etapa: Análise dos resultados e comparação com o Certora Prover.
Contrato Vulnerable
1. Informações Gerais

O contrato Vulnerable é um token ERC20 que inclui funcionalidades adicionais como controle de propriedade, pausabilidade, vesting, e taxa de transferência. Além disso, permite a criação (mint) e destruição (burn) de tokens pelo proprietário e suporta operações de depósito e retirada de Ether. O contrato contém uma vulnerabilidade de reentrância intencional na função de retirada (withdraw).
2. Função Withdraw

solidity

function withdraw(uint256 amount) external whenNotPaused {
    require(userBalances[msg.sender] >= amount, "Insufficient balance");

    uint256 oldBalance = address(this).balance;

    // Atualiza o saldo do usuário antes de enviar o valor
    userBalances[msg.sender] = userBalances[msg.sender].sub(amount);

    // Envia o valor ao usuário
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");

    assert(address(this).balance == oldBalance - amount);

    emit Withdrawn(msg.sender, amount);
}

    Descrição: Ao utilizar call, o valor é enviado ao usuário, permitindo que ele execute código antes que a função original termine. Isso possibilita que o usuário chame a função withdraw novamente antes que o saldo seja atualizado, resultando na retirada de mais fundos do que o disponível. Esta vulnerabilidade é semelhante ao ataque ocorrido no DAO em 2016.

3. Situação Inicial

    Ao compilar o OriginalContract.sol, o SMT Checker pode não identificar o erro ou entrar em um loop eterno, dependendo das configurações de timeout.

4. Simplificação do Código

Para otimizar o contrato para o model-checker, foram realizadas as seguintes fases:
4.1. Compreensão e Divisão

O contrato Vulnerable pode ser dividido em cinco partes independentes:

    ERC20: totalSupply, balanceOf, transfer, allowance, approve, transferFrom.
    Admin: mint, burn, pause, unpause, setTransferTaxRate, setGovernanceContract.
    Vesting: startVesting, claimVestedTokens.
    Depósito e Saque: deposit, withdraw.
    Consulta: getContractBalance.

A otimização deve focar apenas na parte de Depósito e Saque, onde a vulnerabilidade de reentrância ocorre.
4.2. Remoção

Antes de remover funções, analise os módulos restantes:

    ERC20: Define funções e eventos padrão para um token ERC20.
    SafeMath: Fornece operações matemáticas seguras.
    Ownable: Controla a propriedade do contrato.
    Pausable: Permite que o contrato seja pausado e despausado, utilizado principalmente em vesting e operações de depósito e saque, mas não é estritamente necessário.

Conclusão: O contrato otimizado deve manter apenas as funções deposit, withdraw e getContractBalance, além da biblioteca SafeMath.




   




