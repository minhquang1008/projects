/*MTD - BOM - PhaiSinh*/

/*Total branches - Fee Income (Phí giao dịch - by branch, pie chart) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

WITH

[TargetByBranch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Fee Income'
        AND [Year] = YEAR(@Date)
)

, [Rel] AS (
    SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
    WHERE [date] BETWEEN @FirstDateOfMonth AND @Date
)

, [ValueTotalBranches] AS (
	SELECT 
		[Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[PhiGiaoDichPHSThu]) [FeeIncome]
	FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
		AND [RRE0018].[Ngay] = [Rel].[date]
    WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonth AND @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
    GROUP BY [Rel].[BranchID]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [FeeIncome]
		, CASE [FeeIncome] 
			WHEN 0 THEN 0
			ELSE CAST([FeeIncome] / SUM([FeeIncome]) OVER() AS DECIMAL(7,6))
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT 
	[Contribution].[BranchID],
	ISNULL([FeeIncome], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Contribution]
ORDER BY 2 DESC


END