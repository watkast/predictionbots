---
title: "Insider trading on prediction markets: how it works, how it gets caught, and what it costs the other side of the trade"
updated: 2026-11-08
summary: "A prediction market pays whoever knows the answer first. That makes nonpublic information worth exactly the contract's price gap, and it makes the person on the other side of an insider's trade the one who pays. The 2026 cases (a DOJ indictment, exchange suspensions of candidates betting on their own races, CFTC surveillance letters), the rules that now apply, and what a market looks like before a leak."
faq: ["Is insider trading illegal on prediction markets?|Trading on material nonpublic information in event contracts can violate the Commodity Exchange Act's anti-fraud and anti-manipulation rules, and for government employees, specific provisions against using nonpublic government information for personal gain. In April 2026 the Department of Justice and the CFTC brought parallel criminal and civil cases over trades on Polymarket.", "Can a candidate bet on their own election on Kalshi?|No. Kalshi Rule 5.17(z) bars people who can influence an event's outcome from trading its contracts. In April 2026 Kalshi suspended three congressional and state candidates for five years for trading on their own races, with fines and disgorgement.", "How do exchanges detect insider trading?|Through surveillance of account activity and trade patterns, know-your-customer records tying accounts to identities, and, on Polymarket, blockchain analytics (a Chainalysis partnership announced 30 April 2026). The CFTC told platforms in early 2026 that they have an independent duty to keep audit trails and police prohibited practices.", "Who loses when someone trades on inside information?|The counterparty: whoever sold the contract to the insider at a price that did not reflect the information. In a two-sided market every insider profit is someone else's loss, usually spread over many ordinary traders."]
---

A prediction market is a machine for paying whoever knows the answer first. Most of the time that is a forecaster who read the data better. Sometimes it is a person who already knows, and the market cannot tell the difference until afterwards.

## Why the incentive is exact

A contract on "will X happen by Friday" trades at, say, 20¢. Someone who knows X is going to happen can buy at 20¢ and collect $1: a 400% return in days, with no risk on the outcome. The only risks are getting filled (a thin book moves against size) and getting caught. The price gap is the entire incentive, and every cent of it comes from the people who sold at 20¢ because they did not know.

That second part is what the "victimless" framing misses. In a sportsbook, the house takes the other side. In a prediction market, other traders do, and an insider's profit is paid by the ordinary accounts on the other side of the book.

## What 2026 brought

**A criminal case.** On 23 April 2026 the Department of Justice unsealed an indictment in the Southern District of New York, and the CFTC filed a parallel civil complaint, against an active-duty U.S. Army service member accused of trading Polymarket contracts on the Venezuelan president's fate using classified information about U.S. operations. The complaint describes profits of more than $400,000, placed hours before the operation, followed by withdrawals routed through a foreign crypto vault, an exchange and a brokerage account, and a request to delete the account. The charges include commodities fraud, wire fraud, theft of nonpublic government information and unlawful monetary transactions. (CFTC v. Van Dyke, No. 26-cv-3369; United States v. Van Dyke, No. 26 Cr. 156.)

**Candidates betting on themselves.** On 22 April 2026 Kalshi announced disciplinary actions under its Rule 5.17(z), which bars anyone who can influence an event's outcome from trading on it. A state senator running for Congress, a House primary candidate and a Senate primary candidate had each traded on their own race, in amounts from about $50 to a few hundred dollars. Two settled for five-year suspensions and fines; one contested and received a five-year suspension, a $6,229 penalty and disgorgement. The sums were small; the rule is not.

**The regulator's letters.** CFTC Enforcement Release 9185-26 (25 February 2026) and Staff Letter 26-08 (12 March 2026) told platforms they have an independent duty to maintain audit trails, run surveillance and enforce their rules against prohibited practices. Congress opened its own inquiry, and regulators requested trading records from both Kalshi and Polymarket over suspicious political bets.

**The platforms' answers.** Kalshi moved in March 2026 to block athletes, coaches, officials and political candidates from trading on their own events. Polymarket announced a partnership with Chainalysis on 30 April 2026 to detect insider trading and suspicious activity on-chain.

## How it gets caught

1. **The pattern.** A new or dormant account, a large position in a thin market, placed shortly before the news, often in a contract nobody else is trading. Surveillance systems flag exactly this; so do other traders, who post the wallet or the account on X within hours.
2. **The identity.** Kalshi and Polymarket US accounts are opened with ID verification. On the international Polymarket book, wallets are pseudonymous but public, and analytics firms follow the money from the wallet to the exchange where it was cashed out.
3. **The record.** Every order and fill is logged with a timestamp. Once an investigator has the account, the question is only when the trader knew, which is a question for subpoenas, not screenshots.

## What a market looks like before a leak

Our recorder stores prices and order books at one-second resolution for the markets we cover, so we can say precisely what "the market moved before the news" means in those cases: a jump in price on thin volume, minutes to hours before any public report, followed by a rush when the report lands. We publish those paths when they occur, with the data, and never a name without a filing behind it. The pattern is public; the accusation is the court's to make.

## What it means for you

- If a market moves hard on no news, the most likely explanation is that someone knows something, and the person selling to them is usually an ordinary trader who does not.
- Betting on an event you can influence is a rule violation on Kalshi and a potential federal offence if the information is nonpublic and yours by virtue of your job.
- The honest version of "edge" is public information plus better analysis. Everything else is somebody else's money with a paper trail.

*Sources: DOJ and CFTC filings of 23 April 2026 as summarized in legal reporting (Mondaq, 5 May 2026); Kalshi disciplinary notices KDA-2026-0004, KDA-2026-0005 and KE-2026-0003; CFTC Release 9185-26 and Staff Letter 26-08; Polymarket announcement of 30 April 2026. Read 8 November 2026. Nothing here is legal advice.*
