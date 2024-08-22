# Pesquisa - Verificação Formal de Contratos Inteligentes

**Esse projeto visa demonstrar a funcionalidade do SMT Checker em contratos onde há explosão de dados, e comparar sua atuação com as outras ferramentas de verificação formal da indústria.**

## Metodologia

**1ª Etapa**: Criação de um contrato inteligente com vulnerabilidade proposital, mas que o SMT Checker não consiga detectá-la.

**2ª Etapa**: Simplificação do código com preservação semântica, visando facilitar o caminho que o model-checker percorrerá.

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
   
   -   Ao utilizar 'call', o valor é enviado ao usuário, mas permite que ele possa executar um código arbitário antes que a função original termine. Assim, o usuário pode chamar o withdraw    novamente antes que a primeira chamada termine, retirando mais fundos do que possui, já que o saldo ainda não foi atualizado na segunda chamada. Dessa forma, um hacker pode criar um contrato malicioso que chama repetidamente a função withdraw, como ocorreu no DAO em 2016.

   




