/*YTD*/

/*Headline Tag - New Accounts (Phần trăm hoàn thành chỉ tiêu tháng - Tài khoản mở mới) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfCurrentYear DATETIME;
SET @FirstDateOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfPreviousYear DATETIME;
SET @FirstDateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),1,1,0,0,0,0));

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
	WHERE ([date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear)
		OR ([date] BETWEEN @FirstDateOfCurrentYear AND @Date)
)

, [ValueByBranchOfPreviousPeriod] AS (
	SELECT
		[Rel].[BranchID]
		, COUNT(*) [NewAccounts]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[Date] = [customer_change].[open_date]
	WHERE [customer_change].[open_date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
	GROUP BY [Rel].[BranchID]
)

, [ValueByBranchOfCurrentPeriod] AS (
	SELECT
		[Rel].[BranchID]
		, COUNT(*) [NewAccounts]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[date] = [customer_change].[open_date]
	WHERE [customer_change].[open_date] BETWEEN @FirstDateOfCurrentYear AND @Date
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
	GROUP BY [Rel].[BranchID]
)

, [result] AS (
	SELECT 
		[BranchTarget].[BranchID]
		, ISNULL([ValueByBranchOfCurrentPeriod].[NewAccounts],0) [NewAccounts]
		, CAST(ISNULL([ValueByBranchOfCurrentPeriod].[NewAccounts],0) AS DECIMAL(10,5)) - CAST(ISNULL([ValueByBranchOfPreviousPeriod].[NewAccounts],0) AS DECIMAL(10,5)) [AbsoluteChange] 
		, CASE ISNULL([ValueByBranchOfPreviousPeriod].[NewAccounts],0) WHEN 0 THEN 0
			ELSE CAST(ISNULL([ValueByBranchOfCurrentPeriod].[NewAccounts],0) AS DECIMAL(10,5)) / CAST([ValueByBranchOfPreviousPeriod].[NewAccounts] AS DECIMAL(10,5)) - 1 
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [ValueByBranchOfPreviousPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfPreviousPeriod].[BranchID]
	LEFT JOIN [ValueByBranchOfCurrentPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfCurrentPeriod].[BranchID]
)

SELECT
	SUM([NewAccounts]) [NewAccounts],
	SUM([AbsoluteChange]) [AbsoluteChange],
	SUM([RelativeChange]) [RelativeChange]
FROM [result]


END
