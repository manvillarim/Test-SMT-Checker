# Pesquisa - Verificação Formal de Contratos Inteligentes

**Esse projeto visa demonstrar a funcionalidade do SMT Checker em contratos onde há explosão de dados, e comparar sua atuação com as outras ferramentas de verificação formal da indústria.**

## Metodologia

**1ª Etapa**: Criação de um contrato inteligente com vulnerabilidade proposital, mas que o SMT Checker não consiga detectá-la.

**2ª Etapa**: Simplificação do código com preservação semântica, visando simplificar o caminho que o model-checker percorrerá.

**3ª Etapa**: Resultados e comparação com o Certora Prover.

## Contrato Vulnerabilities

1. **Informações Gerais**
   - Um token ERC20 que adiciona funcionalidades como controle de propriedade com o Ownable, pausabilidade com o Pausable, que permite pausar e retomar as funções do contrato; e um mecanismo de vesting que libera tokens ao longo do tempo para endereços específicos. Além disso, inclui uma taxa de transferência que é deduzida em cada transação e enviada ao proprietário, além de permitir a criação (mint) e destruição (burn) de tokens pelo proprietário. O contrato também suporta operações de depósito e retirada de Ether, com uma vulnerabilidade de reentrância intencional na função de retirada (withdraw).


