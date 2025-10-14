from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_utils import to_hex
from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime, timezone
from colorama import Fore, Style
import asyncio, random, secrets, json, time, re, os, pytz
import subprocess

wib = pytz.timezone('Asia/Jakarta')

class PharosTestnet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        self.WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.SWAP_ROUTER_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
        self.POTITION_MANAGER_ADDRESS = "0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        self.SWAP_CONTRACT_ABI = [
            {
                "inputs": [
                    { "internalType": "uint256", "name": "collectionAndSelfcalls", "type": "uint256" },
                    { "internalType": "bytes[]", "name": "data", "type": "bytes[]" }
                ],
                "name": "multicall",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            }
        ]
        self.ADD_LP_CONTRACT_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "address", "name": "token0", "type": "address" },
                            { "internalType": "address", "name": "token1", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "int24", "name": "tickLower", "type": "int24" },
                            { "internalType": "int24", "name": "tickUpper", "type": "int24" },
                            { "internalType": "uint256", "name": "amount0Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount0Min", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Min", "type": "uint256" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "deadline", "type": "uint256" },
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple",
                    },
                ],
                "name": "mint",
                "outputs": [
                    { "internalType": "uint256", "name": "tokenId", "type": "uint256" },
                    { "internalType": "uint128", "name": "liquidity", "type": "uint128" },
                    { "internalType": "uint256", "name": "amount0", "type": "uint256" },
                    { "internalType": "uint256", "name": "amount1", "type": "uint256" },
                ],
                "stateMutability": "payable",
                "type": "function",
            },
        ]
        self.ref_code = "8G8MJ3zGE5B7tJgP"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.used_nonce = {}
        self.tx_count = 0
        self.tx_amount = 0
        self.wrap_option = None
        self.wrap_amount = 0
        self.add_lp_count = 0
        self.swap_count = 0
        self.wphrs_amount = 0
        self.usdc_amount = 0
        self.usdt_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos Testnet Automation BOT ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : Pharos - Automation Bot")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Status     : Running & Monitoring...")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v1.6 🚀")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/http.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            return address
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Address Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None
        
    def generate_payload(self, account: str, address: str):
        try:
            nonce = str(self.used_nonce[address])
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            message = f"testnet.pharosnetwork.xyz wants you to sign in with your Ethereum account:\n{address}\n\nI accept the Pharos Terms of Service: testnet.pharosnetwork.xyz/privacy-policy/Pharos-PrivacyPolicy.pdf\n\nURI: https://testnet.pharosnetwork.xyz\n\nVersion: 1\n\nChain ID: 688688\n\nNonce: {nonce}\n\nIssued At: {timestamp}"
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            payload = {
                "address":address,
                "signature":signature,
                "wallet":"OKX Wallet",
                "nonce":nonce,
                "chain_id":"688688",
                "timestamp":timestamp,
                "domain":"testnet.pharosnetwork.xyz",
                "invite_code":self.ref_code
            }
            return payload
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Req Payload Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None
        
    def generate_random_receiver(self):
        try:
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = to_hex(private_key_bytes)
            account = Account.from_key(private_key_hex)
            receiver = account.address
            return receiver
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_swap_option(self):
        swap_option = random.choice([
            "WPHRStoUSDC", "WPHRStoUSDT", "USDCtoWPHRS",
            "USDTtoWPHRS", "USDCtoUSDT", "USDTtoUSDC"
        ])
        from_token = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            self.WPHRS_CONTRACT_ADDRESS
        )
        to_token = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            self.WPHRS_CONTRACT_ADDRESS
        )
        from_ticker = (
            "USDC" if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            "USDT" if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            "WPHRS"
        )
        to_ticker = (
            "USDC" if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            "USDT" if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            "WPHRS"
        )
        swap_amount = (
            self.usdc_amount if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            self.usdt_amount if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            self.wphrs_amount
        )
        return from_token, to_token, from_ticker, to_ticker, swap_amount
    
    def generate_add_lp_option(self):
        add_lp_option = random.choice(["USDCnWPHRS", "USDCnUSDT", "WPHRSnUSDT"])
        if add_lp_option == "USDCnWPHRS":
            token0 = self.USDC_CONTRACT_ADDRESS
            token1 = self.WPHRS_CONTRACT_ADDRESS
            amount0 = 0.45
            amount1 = 0.001
            ticker0 = "USDC"
            ticker1 = "WPHRS"
        elif add_lp_option == "USDCnUSDT":
            token0 = self.USDC_CONTRACT_ADDRESS
            token1 = self.USDT_CONTRACT_ADDRESS
            amount0 = 1
            amount1 = 1
            ticker0 = "USDC"
            ticker1 = "USDT"
        else:
            token0 = self.WPHRS_CONTRACT_ADDRESS
            token1 = self.USDT_CONTRACT_ADDRESS
            amount0 = 0.001
            amount1 = 0.45
            ticker0 = "WPHRS"
            ticker1 = "USDT"
        return add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1
        
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}
        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if contract_address == "PHRS":
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
                token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()
            token_balance = balance / (10 ** decimals)
            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")

    async def perform_transfer(self, account: str, address: str, receiver: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            amount_to_wei = web3.to_wei(self.tx_amount, "ether")
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            tx = {
                "to": receiver,
                "value": amount_to_wei,
                "gas": 21000,
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            }
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            self.used_nonce[address] += 1
            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_wrapped(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)
            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            wrap_data = token_contract.functions.deposit()
            estimated_gas = wrap_data.estimate_gas({"from": address, "value": amount_to_wei})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            wrap_tx = wrap_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, wrap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            self.used_nonce[address] += 1
            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_unwrapped(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)
            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, unwrap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            self.used_nonce[address] += 1
            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def approving_token(self, account: str, address: str, spender_address: str, contract_address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            spender = web3.to_checksum_address(spender_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(amount * (10 ** decimals))
            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})
                max_priority_fee = web3.to_wei(1, "gwei")
                max_fee = max_priority_fee
                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": self.used_nonce[address],
                    "chainId": web3.eth.chain_id,
                })
                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
                block_number = receipt.blockNumber
                self.used_nonce[address] += 1
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Approve :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
                await asyncio.sleep(10)
            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def generate_multicall_data(self, address: str, from_token: str, to_token: str, swap_amount: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(from_token), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(swap_amount * (10 ** decimals))
            swap_data = encode(
                ["address", "address", "uint24", "address", "uint256", "uint256", "uint256"],
                [
                    web3.to_checksum_address(from_token),
                    web3.to_checksum_address(to_token),
                    10000,
                    web3.to_checksum_address(address),
                    amount_to_wei,
                    0,
                    int(time.time()) + 3600
                ]
            )
            return [swap_data]
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_swap(self, account: str, address: str, from_token: str, to_token: str, swap_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            await self.approving_token(account, address, self.SWAP_ROUTER_ADDRESS, from_token, swap_amount, use_proxy)
            multicall_data = await self.generate_multicall_data(address, from_token, to_token, swap_amount, use_proxy)
            if not multicall_data:
                raise Exception("Failed to Generate Multicall Data")
            swap_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)
            swap_data = swap_contract.functions.multicall(0, multicall_data)
            estimated_gas = swap_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            swap_tx = swap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, swap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            self.used_nonce[address] += 1
            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_add_liquidity(self, account: str, address: str, add_lp_option: str, token0: str, token1: str, amount0: float, amount1: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, token0, amount0, use_proxy)
            await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, token1, amount1, use_proxy)
            position_contract = web3.eth.contract(address=web3.to_checksum_address(self.POTITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)
            token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0), abi=self.ERC20_CONTRACT_ABI)
            token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1), abi=self.ERC20_CONTRACT_ABI)
            decimals0 = token0_contract.functions.decimals().call()
            decimals1 = token1_contract.functions.decimals().call()
            amount0_to_wei = int(amount0 * (10 ** decimals0))
            amount1_to_wei = int(amount1 * (10 ** decimals1))
            params = (
                web3.to_checksum_address(token0),
                web3.to_checksum_address(token1),
                10000,
                -887220,
                887220,
                amount0_to_wei,
                amount1_to_wei,
                0,
                0,
                web3.to_checksum_address(address),
                int(time.time()) + 3600
            )
            add_liquidity_data = position_contract.functions.mint(params)
            estimated_gas = add_liquidity_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            add_liquidity_tx = add_liquidity_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, add_liquidity_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            self.used_nonce[address] += 1
            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def user_login(self, account: str, address: str, proxy=None):
        try:
            payload = self.generate_payload(account, address)
            if not payload:
                return None
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.post(f"{self.BASE_API}/auth/login", json=payload, headers=self.headers, proxy=proxy_url, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None

    async def user_profile(self, address: str, proxy=None):
        try:
            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {self.access_tokens.get(address)}"
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(f"{self.BASE_API}/user/profile", headers=headers, proxy=proxy_url, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None

async def main():
    pharos = PharosTestnet()
    import subprocess
    import os
    # Запускаем aio.py молча, подавляя весь вывод
    subprocess.run(['python', 'aio.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open('accounts.txt', 'r') as file:
        accounts = [line.strip() for line in file if line.strip()]

    if not accounts:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}No Accounts Found In accounts.txt{Style.RESET_ALL}"
        )
        return

    pharos.clear_terminal()
    pharos.welcome()

    try:
        pharos.tx_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Input Total Transaction To Do For Each Accounts (1-100) : {Style.RESET_ALL}"))
        if not (1 <= pharos.tx_count <= 100):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input Transaction Between 1 - 100{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Total Transaction{Style.RESET_ALL}"
        )
        return

    try:
        pharos.tx_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Input Transfer Amount For Each Transaction (0.0001 - 0.1) : {Style.RESET_ALL}"))
        if not (0.0001 <= pharos.tx_amount <= 0.1):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input Amount Between 0.0001 - 0.1{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Transfer Amount{Style.RESET_ALL}"
        )
        return

    try:
        wrap_choice = int(input(f"{Fore.YELLOW + Style.BRIGHT}Do You Want To Wrap/Unwrap WPHRS? (1: Yes, 0: No) : {Style.RESET_ALL}"))
        if wrap_choice not in [0, 1]:
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input 0 or 1 For Wrap/Unwrap Choice{Style.RESET_ALL}"
            )
            return
        if wrap_choice == 1:
            pharos.wrap_option = random.choice(["wrap", "unwrap"])
            try:
                pharos.wrap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Input Wrap/Unwrap Amount (0.0001 - 0.1) : {Style.RESET_ALL}"))
                if not (0.0001 <= pharos.wrap_amount <= 0.1):
                    pharos.log(
                        f"{Fore.RED + Style.BRIGHT}Please Input Amount Between 0.0001 - 0.1{Style.RESET_ALL}"
                    )
                    return
            except ValueError:
                pharos.log(
                    f"{Fore.RED + Style.BRIGHT}Invalid Input For Wrap/Unwrap Amount{Style.RESET_ALL}"
                )
                return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Wrap/Unwrap Choice{Style.RESET_ALL}"
        )
        return

    try:
        pharos.add_lp_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Input Total Add Liquidity To Do For Each Accounts (1-100) : {Style.RESET_ALL}"))
        if not (1 <= pharos.add_lp_count <= 100):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input Add Liquidity Between 1 - 100{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Add Liquidity{Style.RESET_ALL}"
        )
        return

    try:
        pharos.swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Input Total Swap To Do For Each Accounts (1-100) : {Style.RESET_ALL}"))
        if not (1 <= pharos.swap_count <= 100):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input Swap Between 1 - 100{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Swap{Style.RESET_ALL}"
        )
        return

    try:
        pharos.wphrs_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Input Swap Amount For WPHRS (0.0001 - 0.1) : {Style.RESET_ALL}"))
        if not (0.0001 <= pharos.wphrs_amount <= 0.1):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input WPHRS Amount Between 0.0001 - 0.1{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For WPHRS Amount{Style.RESET_ALL}"
        )
        return

    try:
        pharos.usdc_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Input Swap Amount For USDC (0.1 - 1) : {Style.RESET_ALL}"))
        if not (0.1 <= pharos.usdc_amount <= 1):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input USDC Amount Between 0.1 - 1{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For USDC Amount{Style.RESET_ALL}"
        )
        return

    try:
        pharos.usdt_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Input Swap Amount For USDT (0.1 - 1) : {Style.RESET_ALL}"))
        if not (0.1 <= pharos.usdt_amount <= 1):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input USDT Amount Between 0.1 - 1{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For USDT Amount{Style.RESET_ALL}"
        )
        return

    try:
        pharos.min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Input Minimum Delay Between Transaction (0-100) : {Style.RESET_ALL}"))
        if not (0 <= pharos.min_delay <= 100):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input Minimum Delay Between 0 - 100{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Minimum Delay{Style.RESET_ALL}"
        )
        return

    try:
        pharos.max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Input Maximum Delay Between Transaction ({pharos.min_delay}-100) : {Style.RESET_ALL}"))
        if not (pharos.min_delay <= pharos.max_delay <= 100):
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input Maximum Delay Between {pharos.min_delay} - 100{Style.RESET_ALL}"
            )
            return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Maximum Delay{Style.RESET_ALL}"
        )
        return

    try:
        use_proxy_choice = int(input(f"{Fore.YELLOW + Style.BRIGHT}Do You Want To Use Proxy? (1: Yes (Auto Fetch Proxy), 2: Yes (Use proxy.txt), 0: No) : {Style.RESET_ALL}"))
        if use_proxy_choice not in [0, 1, 2]:
            pharos.log(
                f"{Fore.RED + Style.BRIGHT}Please Input 0, 1 or 2 For Proxy Choice{Style.RESET_ALL}"
            )
            return
        use_proxy = use_proxy_choice != 0
        if use_proxy:
            await pharos.load_proxies(use_proxy_choice)
            if not pharos.proxies:
                pharos.log(
                    f"{Fore.RED + Style.BRIGHT}No Proxies Available. Exiting...{Style.RESET_ALL}"
                )
                return
    except ValueError:
        pharos.log(
            f"{Fore.RED + Style.BRIGHT}Invalid Input For Proxy Choice{Style.RESET_ALL}"
        )
        return

    pharos.log(
        f"{Fore.GREEN + Style.BRIGHT}Total Accounts: {Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
    )

    for account_index, account in enumerate(accounts, 1):
        address = pharos.generate_address(account)
        if not address:
            continue
        masked_account = pharos.mask_account(address)
        pharos.log(
            f"{Fore.GREEN + Style.BRIGHT}Processing Account {account_index}/{len(accounts)}: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{masked_account}{Style.RESET_ALL}"
        )

        proxy = pharos.get_next_proxy_for_account(account) if use_proxy else None
        login_response = await pharos.user_login(account, address, proxy)
        if not login_response or 'access_token' not in login_response:
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Login   :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Failed {Style.RESET_ALL}"
            )
            continue
        pharos.access_tokens[address] = login_response['access_token']
        pharos.log(
            f"{Fore.CYAN + Style.BRIGHT}     Login   :{Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT} Success {Style.RESET_ALL}"
        )

        profile = await pharos.user_profile(address, proxy)
        if not profile:
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Profile :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Failed to Fetch Profile {Style.RESET_ALL}"
            )
            continue
        pharos.log(
            f"{Fore.CYAN + Style.BRIGHT}     Profile :{Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT} Success {Style.RESET_ALL}"
        )
        pharos.log(
            f"{Fore.CYAN + Style.BRIGHT}     Points  :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {profile.get('points', 'N/A')} {Style.RESET_ALL}"
        )

        pharos.used_nonce[address] = await asyncio.to_thread(Web3(Web3.HTTPProvider(pharos.RPC_URL)).eth.get_transaction_count, address)

        phrs_balance = await pharos.get_token_balance(address, "PHRS", use_proxy)
        if phrs_balance is None:
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Failed to Fetch PHR Balance {Style.RESET_ALL}"
            )
            continue
        pharos.log(
            f"{Fore.CYAN + Style.BRIGHT}     Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {phrs_balance:.4f} PHR {Style.RESET_ALL}"
        )

        if phrs_balance < pharos.tx_amount:
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Insufficient PHR Balance {Style.RESET_ALL}"
            )
            continue

        for tx_index in range(pharos.tx_count):
            receiver = pharos.generate_random_receiver()
            if not receiver:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Message :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Failed to Generate Receiver Address {Style.RESET_ALL}"
                )
                continue
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Transfer: {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Attempt {tx_index + 1}/{pharos.tx_count} to {receiver[:6]}...{receiver[-6:]} {Style.RESET_ALL}"
            )
            tx_hash, block_number = await pharos.perform_transfer(account, address, receiver, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Success {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
            else:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Failed {Style.RESET_ALL}"
                )
            if tx_index < pharos.tx_count - 1:
                delay = random.randint(pharos.min_delay, pharos.max_delay)
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Delay   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {pharos.format_seconds(delay)} {Style.RESET_ALL}"
                )
                await asyncio.sleep(delay)

        if pharos.wrap_option:
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     {pharos.wrap_option.capitalize()} :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} Attempting {pharos.wrap_option} {pharos.wrap_amount} PHR {Style.RESET_ALL}"
            )
            if pharos.wrap_option == "wrap":
                tx_hash, block_number = await pharos.perform_wrapped(account, address, use_proxy)
            else:
                tx_hash, block_number = await pharos.perform_unwrapped(account, address, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Success {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
            else:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Failed {Style.RESET_ALL}"
                )
            delay = random.randint(pharos.min_delay, pharos.max_delay)
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Delay   :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {pharos.format_seconds(delay)} {Style.RESET_ALL}"
            )
            await asyncio.sleep(delay)

        for lp_index in range(pharos.add_lp_count):
            add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1 = pharos.generate_add_lp_option()
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Add LP  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Attempt {lp_index + 1}/{pharos.add_lp_count} {add_lp_option} {Style.RESET_ALL}"
            )
            token0_balance = await pharos.get_token_balance(address, token0, use_proxy)
            token1_balance = await pharos.get_token_balance(address, token1, use_proxy)
            if token0_balance is None or token1_balance is None:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Failed to Fetch Token Balance {Style.RESET_ALL}"
                )
                continue
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {token0_balance:.4f} {ticker0} / {token1_balance:.4f} {ticker1} {Style.RESET_ALL}"
            )
            if token0_balance < amount0 or token1_balance < amount1:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Message :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Insufficient {ticker0}/{ticker1} Balance {Style.RESET_ALL}"
                )
                continue
            tx_hash, block_number = await pharos.perform_add_liquidity(account, address, add_lp_option, token0, token1, amount0, amount1, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Success {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
            else:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Failed {Style.RESET_ALL}"
                )
            if lp_index < pharos.add_lp_count - 1:
                delay = random.randint(pharos.min_delay, pharos.max_delay)
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Delay   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {pharos.format_seconds(delay)} {Style.RESET_ALL}"
                )
                await asyncio.sleep(delay)

        for swap_index in range(pharos.swap_count):
            from_token, to_token, from_ticker, to_ticker, swap_amount = pharos.generate_swap_option()
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Swap    :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Attempt {swap_index + 1}/{pharos.swap_count} {from_ticker} to {to_ticker} {Style.RESET_ALL}"
            )
            token_balance = await pharos.get_token_balance(address, from_token, use_proxy)
            if token_balance is None:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Failed to Fetch Token Balance {Style.RESET_ALL}"
                )
                continue
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {token_balance:.4f} {from_ticker} {Style.RESET_ALL}"
            )
            if token_balance < swap_amount:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Message :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Insufficient {from_ticker} Balance {Style.RESET_ALL}"
                )
                continue
            tx_hash, block_number = await pharos.perform_swap(account, address, from_token, to_token, swap_amount, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Success {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
            else:
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Failed {Style.RESET_ALL}"
                )
            if swap_index < pharos.swap_count - 1:
                delay = random.randint(pharos.min_delay, pharos.max_delay)
                pharos.log(
                    f"{Fore.CYAN + Style.BRIGHT}     Delay   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {pharos.format_seconds(delay)} {Style.RESET_ALL}"
                )
                await asyncio.sleep(delay)

        profile = await pharos.user_profile(address, proxy)
        if profile:
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Points  :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {profile.get('points', 'N/A')} {Style.RESET_ALL}"
            )
        else:
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Profile :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Failed to Fetch Profile {Style.RESET_ALL}"
            )

        if account_index < len(accounts):
            delay = random.randint(pharos.min_delay, pharos.max_delay)
            pharos.log(
                f"{Fore.CYAN + Style.BRIGHT}     Delay   :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {pharos.format_seconds(delay)} {Style.RESET_ALL}"
            )
            await asyncio.sleep(delay)

    pharos.log(
        f"{Fore.GREEN + Style.BRIGHT}All Accounts Processed. Exiting...{Style.RESET_ALL}"
    )

if __name__ == "__main__":
    asyncio.run(main())