# Pesquisa - Verificação Formal de Contratos Inteligentes

**Esse projeto visa demonstrar a funcionalidade do SMT Checker em contratos onde há explosão de dados.**

## Metodologia

**1ª Etapa**: Criação de um contrato inteligente com vulnerabilidade proposital, mas que o SMT Checker não consiga detectá-la.

**2ª Etapa**: Simplificação do código com preservação semântica, visando facilitar o caminho que o model-checker percorrerá.

**3ª Etapa**: Resultados

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

   
   -   Ao utilizar 'call', o valor é enviado ao usuário, mas permite que ele possa executar um código antes que a função original acabe. Assim, o usuário pode chamar o withdraw novamente antes que a primeira chamada termine, retirando mais fundos do que possui, já que o saldo ainda não foi atualizado na segunda chamada. Dessa forma, um hacker pode criar um contrato malicioso que chama repetidamente a função withdraw, como ocorreu no DAO em 2016.

  
3. **Situação Inicial**

   - Ao compilar o 'OriginalContract.sol', o SMT ou não consegue identificar o erro ou entra em loop eterno, dependendo de como o timeout está configurado.
  
4. **Simplificação do Código**

   - Para otimizar o contrato visando o funcionamento do model-checker, 2 fases foram feitas:
  
     1. **Compreensão e divisão**:

       - Podemos dividir o contrato Vulnerabilities em 5 partes independentes com suas respectivas funções:
         
          - ERC20: totalSupply, balanceOf, transfer, allowance, approve, transferFrom.
          - Admin: mint, burn, pause, unpause, setTransferTaxRate, setGovernanceContract.
          - Vesting: startVesting, claimVestedTokens.
          - Depósito e Saque: deposit, withdraw.
          - Consulta: getContractBalance.
       
          - Assim, vê-se que devemos otimizar o código de modo que apenas o Depósito e Saque esteja funcionando, uma vez que o erro da reentrância ocorre nessa parte.
    
     2. **Remoção**:
    
        - Antes de apagar as funções que não façam parte do Depósito e Saque, também se deve analisar os outros módulos do arquivo:
       
           - ERC20: Define as funções e eventos padrão para um token ERC20. --> Utilizado pelo ERC20
           - SafeMath: Fornece operações matemáticas seguras. --> Utilizado em todo o contrato
           - Ownable: Controla a propriedade do contrato. --> Utilizado pelo vesting e admin
           - Pausable: Permite que o contrato seja pausado e despausado. --> utilizado pelo vesting e Depósito e saque, mas não é estritamente necessário
          
           - Assim, podemos deixar apenas as funções deposit, withdraw e getContractBalance, além de bliblioteca SafeMath, otimizando ao máximo.
         
5. **Resultados**

   - Após as modificações, o SMT checker identifica com perfeição a vulnerabilidade do contrato:
  
     ![Imagem do Projeto](https://github.com/manvillarim/Test-SMT-Checker/blob/main/lib/Captura%20de%20tela%20de%202024-08-22%2011-49-19.png)

   - Assim, percebe-se que o SMT checker é capaz de identificar vulnerabilidades em contratos inteligentes de escopo maior, a partir de uma otimização direcionada ao problema que se quer analisar.
