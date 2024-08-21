// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Nesse contrato foram adicionadas funções inúteis e um aumento desnecessário das complexidades das transações
// O SMT não garante mais o erro
// Meta: alterar o contrato sem alteração semântica para o smt voltar a funcionar

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

library SafeMath {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "SafeMath: addition overflow");
        return c;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        return sub(a, b, "SafeMath: subtraction overflow");
    }

    function sub(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
        require(b <= a, errorMessage);
        return a - b;
    }

    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a == 0) {
            return 0;
        }
        uint256 c = a * b;
        require(c / a == b, "SafeMath: multiplication overflow");
        return c;
    }

    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        return div(a, b, "SafeMath: division by zero");
    }

    function div(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
        require(b > 0, errorMessage);
        return a / b;
    }
}

abstract contract Ownable {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor() {
        _owner = msg.sender;
        emit OwnershipTransferred(address(0), _owner);
    }

    function owner() public view returns (address) {
        return _owner;
    }

    modifier onlyOwner() {
        require(owner() == msg.sender, "Ownable: caller is not the owner");
        _;
    }
}

abstract contract Pausable is Ownable {
    event Paused(address account);
    event Unpaused(address account);

    bool private _paused;

    constructor() {
        _paused = false;
    }

    function paused() public view returns (bool) {
        return _paused;
    }

    modifier whenNotPaused() {
        require(!_paused, "Pausable: paused");
        _;
    }

    modifier whenPaused() {
        require(_paused, "Pausable: not paused");
        _;
    }

    function _pause() internal whenNotPaused {
        _paused = true;
        emit Paused(msg.sender);
    }

    function _unpause() internal whenPaused {
        _paused = false;
        emit Unpaused(msg.sender);
    }
}

contract Vulnerable is IERC20, Ownable, Pausable {
    using SafeMath for uint256;

    string public constant name = "ComplexVulnerableToken";
    string public constant symbol = "CVTKN";
    uint8 public constant decimals = 18;
    uint256 private _totalSupply;

    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    mapping(address => uint256) public userBalances;
    mapping(address => uint256) public vestingStart;
    mapping(address => uint256) public vestingEnd;
    mapping(address => uint256) public vestingAmount;

    uint256 public transferTaxRate;
    address public governanceContract;

    uint256 private _initialBalance;
    uint256 private _randomSeed = 0;

    event Minted(address indexed account, uint256 amount);
    event Burned(address indexed account, uint256 amount);
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event TaxRateUpdated(uint256 newRate);
    event GovernanceContractUpdated(address newGovernanceContract);
    event VestingStarted(address indexed account, uint256 start, uint256 end);
    event VestingClaimed(address indexed account, uint256 amount);

    constructor(uint256 initialSupply) {
        _totalSupply = initialSupply * 10 ** uint256(decimals);
        _balances[msg.sender] = _totalSupply;
        _initialBalance = address(this).balance;
        transferTaxRate = 0; // No tax by default
        governanceContract = address(0);
    }

    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }

    function transfer(address recipient, uint256 amount) public override whenNotPaused returns (bool) {
        uint256 taxAmount = amount.mul(transferTaxRate).div(100);
        uint256 amountAfterTax = amount.sub(taxAmount);

        require(amount <= _balances[msg.sender], "Insufficient balance");
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        _balances[recipient] = _balances[recipient].add(amountAfterTax);
        emit Transfer(msg.sender, recipient, amountAfterTax);

        if (taxAmount > 0) {
            _balances[owner()] = _balances[owner()].add(taxAmount);
            emit Transfer(msg.sender, owner(), taxAmount);
        }

        return true;
    }

    function allowance(address owner, address spender) public view override returns (uint256) {
        return _allowances[owner][spender];
    }

    function approve(address spender, uint256 amount) public override whenNotPaused returns (bool) {
        _allowances[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address sender, address recipient, uint256 amount) public override whenNotPaused returns (bool) {
        uint256 taxAmount = amount.mul(transferTaxRate).div(100);
        uint256 amountAfterTax = amount.sub(taxAmount);

        require(amount <= _balances[sender], "Insufficient balance");
        require(amount <= _allowances[sender][msg.sender], "Allowance exceeded");
        _balances[sender] = _balances[sender].sub(amount);
        _balances[recipient] = _balances[recipient].add(amountAfterTax);
        _allowances[sender][msg.sender] = _allowances[sender][msg.sender].sub(amount);
        emit Transfer(sender, recipient, amountAfterTax);

        if (taxAmount > 0) {
            _balances[owner()] = _balances[owner()].add(taxAmount);
            emit Transfer(sender, owner(), taxAmount);
        }

        return true;
    }

    function mint(address account, uint256 amount) external onlyOwner {
        _totalSupply = _totalSupply.add(amount);
        _balances[account] = _balances[account].add(amount);
        emit Minted(account, amount);
    }

    function burn(uint256 amount) external onlyOwner {
        require(amount <= _balances[msg.sender], "Insufficient balance to burn");
        _totalSupply = _totalSupply.sub(amount);
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        emit Burned(msg.sender, amount);
    }

    function pause() external onlyOwner whenNotPaused {
        _pause();
    }

    function unpause() external onlyOwner whenPaused {
        _unpause();
    }

    function setTransferTaxRate(uint256 rate) external onlyOwner {
        require(rate <= 100, "Tax rate cannot exceed 100%");
        transferTaxRate = rate;
        emit TaxRateUpdated(rate);
    }

    function setGovernanceContract(address _governanceContract) external onlyOwner {
        governanceContract = _governanceContract;
        emit GovernanceContractUpdated(_governanceContract);
    }

    function startVesting(address account, uint256 start, uint256 end, uint256 amount) external onlyOwner {
        require(start < end, "Invalid vesting period");
        require(amount <= _balances[address(this)], "Insufficient balance in contract for vesting");
        vestingStart[account] = start;
        vestingEnd[account] = end;
        vestingAmount[account] = amount;
        emit VestingStarted(account, start, end);
    }

    function claimVestedTokens() external whenNotPaused {
        uint256 currentTime = block.timestamp;
        require(currentTime > vestingStart[msg.sender], "Vesting has not started");
        require(currentTime < vestingEnd[msg.sender], "Vesting has ended");

        uint256 totalVestingDuration = vestingEnd[msg.sender] - vestingStart[msg.sender];
        uint256 elapsedVestingDuration = currentTime - vestingStart[msg.sender];
        uint256 vestedAmount = vestingAmount[msg.sender].mul(elapsedVestingDuration).div(totalVestingDuration);

        require(vestedAmount > 0, "No tokens to claim");
        require(vestedAmount <= _balances[address(this)], "Insufficient balance in contract for claim");

        _balances[address(this)] = _balances[address(this)].sub(vestedAmount);
        _balances[msg.sender] = _balances[msg.sender].add(vestedAmount);

        emit VestingClaimed(msg.sender, vestedAmount);
    }

    function deposit() external payable whenNotPaused {
        userBalances[msg.sender] = userBalances[msg.sender].add(msg.value);
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external whenNotPaused {
        require(userBalances[msg.sender] >= amount, "Insufficient balance");

        uint256 currentBalance = address(this).balance;
        uint256 intermediateBalance = currentBalance;

        // Atualiza o saldo do usuário antes de enviar o valor
        userBalances[msg.sender] = userBalances[msg.sender].sub(amount);

        // Envia o valor ao usuário
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        // Manipula a verificação para adicionar complexidade
        uint256 newBalance = address(this).balance;
        uint256 deltaBalance = intermediateBalance.sub(newBalance);

        assert(deltaBalance == amount);

        emit Withdrawn(msg.sender, amount);
    }

    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
