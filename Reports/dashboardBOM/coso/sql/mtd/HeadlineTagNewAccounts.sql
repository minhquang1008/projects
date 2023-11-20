/*MTD*/

/*Headline Tag - New Accounts (Phần trăm hoàn thành chỉ tiêu tháng - Tài khoản mở mới) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonthOfCurrentYear DATETIME;
SET @FirstDateOfMonthOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfMonthOfPreviousYear DATETIME;
SET @FirstDateOfMonthOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),MONTH(@DateOfPreviousYear),1,0,0,0,0));

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
	WHERE ([date] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear)
		OR ([date] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date)
)

, [ValueByBranchOfPreviousPeriod] AS (
	SELECT
		[Rel].[BranchID]
		, COUNT(*) [NewAccounts]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[Date] = [customer_change].[open_date]
	WHERE [customer_change].[open_date] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear
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
	WHERE [customer_change].[open_date] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date
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
