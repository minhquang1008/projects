/*YTD - BOM - PhaiSinh*/

/*Actual vs Target - Fee Income (Phí giao dịch - Thực tế và chỉ tiêu) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfCurrentYear DATETIME;
SET @FirstDateOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

WITH

[TargetByBranch] AS (
	SELECT 
        [BranchID] 
        , CAST(CAST([Target] AS FLOAT) AS DECIMAL(30,8)) [FeeIncome]
    FROM [DWH-AppData].[dbo].[BMD.FDSTarget]
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Fee Income'
)

, [Rel] AS (
    SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
    WHERE [date] BETWEEN @FirstDateOfCurrentYear AND @Date
)

, [BranchActual] AS (
    SELECT 
        [Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[PhiGiaoDichPHSThu]) [FeeIncome]
    FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
    WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfCurrentYear AND @Date
    GROUP BY [Rel].[BranchID]
)

SELECT 
	[TargetByBranch].[BranchID]
	, ISNULL([BranchActual].[FeeIncome],0) [Actual]
    , [TargetByBranch].[FeeIncome] [Target]
FROM [TargetByBranch]
LEFT JOIN [BranchActual]
    ON [TargetByBranch].[BranchID] = [BranchActual].[BranchID]
ORDER BY 1


END
