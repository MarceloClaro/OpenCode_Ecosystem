//SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol";
import './SmartToken.sol';

contract DEX {

    IERC20 public token;

    event Comprado(uint256 quantidadeParaComprada);
    event Vendido(uint256 quantidadeParaVendendida);

    constructor() {
        token = new SmartToken();
    }
    function comprar() payable public {
        uint256 quantidadeParaComprar = msg.value;
        uint256 SaldoDoDEX = token.balanceOf(address(this));
        require(quantidadeParaComprar > 0, "Voce precisa enviar um pouco de Wei");
        require(quantidadeParaComprar <= SaldoDoDEX, "Nao ha tokens suficientes na reserva");
        token.transfer(msg.sender, quantidadeParaComprar);
        emit Comprado(quantidadeParaComprar);
    }

    function vender(uint256 quantidadeParaVender) public {
        require(quantidadeParaVender > 0, "Voce precisa vender pelo menos um token");
        uint256 quantidadeConcedidaParaVender = token.allowance(msg.sender, address(this));
        require(quantidadeConcedidaParaVender >= quantidadeParaVender, "Verifique a concessao (allowance) de token");
        token.transferFrom(msg.sender, address(this), quantidadeParaVender);
        payable(msg.sender).transfer(quantidadeParaVender);
        emit Vendido(quantidadeParaVender);
    }

}