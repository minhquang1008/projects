/*YTD*/

/* Actual vs Target - New Accounts (Tài khoản mở mới - Thực tế và chỉ tiêu) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

WITH

[BranchTarget] AS (
    SELECT 
        [BranchID] 
        , CAST([Target] AS DECIMAL(8,2)) [NewAccounts]
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
	WHERE [date] BETWEEN @FirstDateOfYear AND @Date
)

, [BranchActual] AS (
	SELECT
		[Rel].[BranchID]
		, CAST(COUNT(*) AS DECIMAL(8,2)) [NewAccounts]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[date] = [customer_change].[open_date]
	WHERE [customer_change].[open_date] BETWEEN @FirstDateOfYear AND @Date
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
	GROUP BY [Rel].[BranchID]
)

SELECT
	[BranchTarget].[BranchID]
	, SUM(ISNULL([BranchActual].[NewAccounts],0)) [Actual]
    , SUM([BranchTarget].[NewAccounts]) [Target]
FROM [BranchTarget]
LEFT JOIN [BranchActual]
    ON [BranchTarget].[BranchID] = [BranchActual].[BranchID]
GROUP BY [BranchTarget].[BranchID]


END