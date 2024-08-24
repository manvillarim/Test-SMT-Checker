# Pesquisa - Verificação Formal de Contratos Inteligentes

**Esse projeto visa demonstrar a funcionalidade do SMT Checker em contratos onde há explosão de dados.**

## Metodologia

**1ª Etapa:** Criação de um contrato inteligente com uma vulnerabilidade proposital que não é detectada pelo SMT Checker.

**2ª Etapa:** Simplificação do código mantendo a semântica para melhorar a capacidade do model-checker de identificar a vulnerabilidade.

**3ª Etapa:** Análise dos resultados obtidos.

## Contrato Vulnerabilities

**1. Informações Gerais**

O contrato `Vulnerable` é um token ERC20 que adiciona funcionalidades como controle de propriedade, pausabilidade, vesting e taxa de transferência. Também permite a criação e destruição de tokens e operações de depósito e retirada de Ether. Este contrato contém uma vulnerabilidade de reentrância intencional na função de retirada (`withdraw`), que será usada para testar a eficácia de ferramentas de verificação formal.

**2. Função Withdraw**

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

A função `withdraw` é projetada para demonstrar uma vulnerabilidade de reentrância. Ao utilizar `call`, o valor é enviado ao usuário, permitindo que ele execute código antes da conclusão da função original. Isso possibilita que o usuário chame `withdraw` novamente antes que o saldo seja atualizado, resultando na retirada de mais fundos do que o disponível. Essa vulnerabilidade pode ser explorada para criar um contrato malicioso que retira repetidamente fundos, como ocorreu no ataque ao DAO em 2016.

**3. Situação Inicial**

Ao compilar o `OriginalContract.sol`, o SMT Checker pode não identificar o erro ou entrar em um loop eterno, dependendo da configuração do timeout.

**4. Simplificação do Código**

Para otimizar o contrato para o model-checker, foram realizadas as seguintes fases:

**4.1. Compreensão e Divisão**

O contrato `Vulnerable` pode ser dividido em cinco partes funcionais:

- **ERC20:** Inclui funções padrão como `totalSupply`, `balanceOf`, `transfer`, `allowance`, `approve`, `transferFrom`.
- **Admin:** Funções para administração como `mint`, `burn`, `pause`, `unpause`, `setTransferTaxRate`, `setGovernanceContract`.
- **Vesting:** Funções para gerenciamento de vesting como `startVesting`, `claimVestedTokens`.
- **Depósito e Saque:** Funções para operações de depósito e saque como `deposit`, `withdraw`.
- **Consulta:** Função para consulta de saldo do contrato com `getContractBalance`.

A otimização foca na parte de **Depósito e Saque**, onde a vulnerabilidade de reentrância ocorre, removendo funções não relacionadas.

**4.2. Remoção**

A remoção de funções não essenciais ajuda a reduzir a complexidade e facilita a análise da vulnerabilidade. Mantivemos:

- **Depósito e Saque:** Funções `deposit`, `withdraw`, `getContractBalance`.
- **SafeMath:** Biblioteca para operações matemáticas seguras.

Outras bibliotecas e funções foram removidas para focar na área crítica do problema.

**5. Resultados**

Após as modificações, o SMT Checker foi capaz de identificar com precisão a vulnerabilidade do contrato:

![Imagem do Projeto](https://github.com/manvillarim/Test-SMT-Checker/blob/main/lib/Captura%20de%20tela%20de%202024-08-22%2011-49-19.png)

Isso demonstra que o SMT Checker é eficaz na identificação de vulnerabilidades em contratos inteligentes, especialmente quando o código é otimizado para focar no problema específico em análise.
