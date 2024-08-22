# Pesquisa - Verificação Formal de Contratos Inteligentes

**Esse projeto visa demonstrar a funcionalidade do SMT Checker em contratos onde há explosão de dados, e comparar sua atuação com as outras ferramentas de verificação formal da indústria.**

## Metodologia

**1ª Etapa**: Criação de um contrato inteligente com vulnerabilidade proposital, mas que o SMT Checker não consiga detectá-la.

**2ª Etapa**: Simplificação do código com preservação semântica, visando simplificar o caminho que o model-checker percorrerá.

**3ª Etapa**: Resultados e comparação com o Certora Prover.

## Contrato Vulnerabilities

1. **Informações Gerais**

   - Um token ERC20 com adição de funcionalidades como controle de propriedade, pausabilidade, vesting e taxa de transferência, além de permitir a criação (mint) e destruição (burn) de tokens pelo proprietário. O contrato também suporta operações de depósito e retirada de Ether, com uma vulnerabilidade de reentrância intencional na função de retirada (withdraw).
  
2. **Função Withdraw**


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
   
   - A vulnerabilidade dessa função pode ser explorada da seguinte forma:
     
    1. Chamada Externa: A linha (bool success, ) = msg.sender.call{value: amount}(""); envia o valor ao usuário, mas permite que o usuário execute código arbitrário (como outra chamada à função withdraw)            antes que a execução da função original termine.

    2. Estado Inconsistente: Se o usuário conseguir chamar withdraw novamente antes que a primeira chamada termine, ele pode retirar mais fundos do que possui, pois o saldo do usuário                                (userBalances[msg.sender]) ainda não foi atualizado na segunda chamada.

    3. Exploração: Um atacante pode criar um contrato malicioso que chama a função withdraw repetidamente dentro de sua função fallback, esvaziando o contrato antes que a primeira chamada termine.

   




