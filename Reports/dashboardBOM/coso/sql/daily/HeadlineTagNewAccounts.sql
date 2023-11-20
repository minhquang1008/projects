/*Daily*/

/*Headline Tag - New Accounts (Phần trăm hoàn thành chỉ tiêu ngày - Tài khoản mở mới) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date]) 
	FROM (
		SELECT TOP 2
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

WITH

[BranchTarget] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'New Accounts'
)

, [Rel] AS (
	SELECT DISTINCT
		[date] [Date]
		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
	WHERE [date] IN (@Prev, @Date)
)

, [PrevValueByBranch] AS (
	SELECT
		[Rel].[BranchID]
		, COUNT(*) [NewAccounts]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[Date] = [customer_change].[open_date]
	WHERE [customer_change].[open_date] = @Prev
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
	GROUP BY [Rel].[BranchID]
)

, [TodayValueByBranch] AS (
	SELECT
		[Rel].[BranchID]
		, COUNT(*) [NewAccounts]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[date] = [customer_change].[open_date]
	WHERE [customer_change].[open_date] = @Date
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
	GROUP BY [Rel].[BranchID]
)

, [result] AS (
	SELECT 
		[BranchTarget].[BranchID]
		, ISNULL([TodayValueByBranch].[NewAccounts],0) [NewAccounts]
		, CAST(ISNULL([TodayValueByBranch].[NewAccounts],0) AS DECIMAL(10,5)) - CAST(ISNULL([PrevValueByBranch].[NewAccounts],0) AS DECIMAL(10,5)) [AbsoluteChange] 
		, CASE ISNULL([PrevValueByBranch].[NewAccounts],0) WHEN 0 THEN 0
			ELSE CAST(ISNULL([TodayValueByBranch].[NewAccounts],0) AS DECIMAL(10,5)) / CAST([PrevValueByBranch].[NewAccounts] AS DECIMAL(10,5)) - 1 
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [PrevValueByBranch]
		ON [BranchTarget].[BranchID] = [PrevValueByBranch].[BranchID]
	LEFT JOIN [TodayValueByBranch]
		ON [BranchTarget].[BranchID] = [TodayValueByBranch].[BranchID]
)

SELECT
	SUM([NewAccounts]) [NewAccounts],
	SUM([AbsoluteChange]) [AbsoluteChange],
	SUM([RelativeChange]) [RelativeChange]
FROM [result]


END
