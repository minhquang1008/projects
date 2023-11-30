/*YTD - BOM - PhaiSinh*/

/*Total branches - Fee Income (Phí giao dịch - by branch, pie chart) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

WITH

[Branch] AS (
    SELECT DISTINCT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
)

, [TargetByBranch] AS (
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
    WHERE [date] BETWEEN @FirstDateOfYear AND @Date
)

, [ValueTotalBranches] AS (
	SELECT 
		[Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[PhiGiaoDichPHSThu]) [FeeIncome]
	FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
		AND [RRE0018].[Ngay] = [Rel].[date]
    WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfYear AND @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
    GROUP BY [Rel].[BranchID]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [FeeIncome]
		, CASE [FeeIncome] 
			WHEN 0 THEN 0
			ELSE [FeeIncome] / (SELECT SUM([FeeIncome]) FROM [ValueTotalBranches])
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT
	RANK() OVER(ORDER BY ISNULL([FeeIncome], 0) DESC) [Rank]
	, [Branch].[BranchID]
	, ISNULL([FeeIncome], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]
ORDER BY 1


END