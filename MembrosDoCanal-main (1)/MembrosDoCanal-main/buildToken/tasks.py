from textwrap import dedent
from crewai import Task

class Tasks():
	def code_task(self, agent, task):
		return Task(description=dedent(f"""You will create a new token for a blockchain plataform, these are the instructions:

			Instructions
			------------
    	{task}

			Your final response should be the complete smart contract code programming using the user-entered blockchain platform programming language. For example, if the platform is Ethereum or Binance Smart Chain use the Solidity language, if the blockchain platform is Solana use the Rust language, if the blockchain platform is Tron use the Solidy language.
			"""),
			agent=agent
		)

	def review_task(self, agent, task):
		return Task(description=dedent(f"""\
			You are helping create a new token, these are the instructions:

			Instructions
			------------
			{task}

			Using the code you got, check for errors. Check for logic errors,
			syntax errors, missing imports, variable declarations, mismatched brackets,
			and security vulnerabilities.

			Your final response should be the complete smart contract code created and also the audit result displayed as a numbered list.
			"""),
			agent=agent
		)

	